import random

from django.db.models import F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from manager.models import Source


class GetRandomTargetsApiView(APIView):
    # TODO: implement auth

    def get(self, request):

        sources = Source.objects.raw("""
            SELECT
                "manager_source"."id",
                "manager_source"."name",
                "manager_source"."url",
                "manager_source"."limit",
                "manager_source"."is_active",
                (
                    SELECT SUM("traffic") AS "traffic_count"
                    FROM (
                        SELECT "traffic" FROM "manager_target" WHERE "source_id" = "manager_source"."id" ORDER BY "publish_time" DESC LIMIT 5
                    )
                ) AS "traffic_count"
            FROM "manager_source"
            WHERE (
                "manager_source"."is_active"
                AND "traffic_count" < "manager_source"."limit"
            )
        """)

        random_targets = []

        for source in sources:
            # NOTE: Could move this operation to shared task
            target = random.choice(source.targets.order_by('-publish_time')[:5])
            target.traffic = F('traffic') + 1
            target.save()

            random_targets.append(target.url)

        return Response(data=random_targets, status=status.HTTP_200_OK)
