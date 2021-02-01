import random

from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from manager.models import Source, StaticTarget


class GetRandomTargetsApiView(APIView):
    permission_classes = [HasAPIKey]

    def get(self, request):

        sources = Source.objects.raw("""
            SELECT
                ms.id
                -- ms.name,
                -- ms.url,
                -- ms.limit,
                -- ms.is_active,
                -- tc.traffic_count
            FROM manager_source ms
            INNER JOIN (
                SELECT
                    manager_source.id AS ms_id,
                    (
                        SELECT SUM(traffic_list.traffic)
                        FROM (
                            SELECT
                                manager_target.traffic AS traffic
                            FROM manager_target
                            WHERE manager_target.source_id = manager_source.id
                            ORDER BY publish_time DESC
                            LIMIT 5
                        ) AS traffic_list
                    ) AS traffic_count
                FROM manager_source
            ) AS tc
            ON tc.ms_id = ms.id
            WHERE (
                ms.is_active
                AND
                tc.traffic_count < ms.limit
            )
        """)

        random_targets = []

        for source in sources:
            # NOTE: Could move this operation to shared task
            target = random.choice(source.targets.order_by('-publish_time')[:5])
            target.traffic = F('traffic') + 1
            target.save()

            random_targets.append(target.url)

        random_targets.extend(StaticTarget.objects.filter(is_active=True).values_list('url', flat=True))

        return Response(data=random_targets, status=status.HTTP_200_OK)
