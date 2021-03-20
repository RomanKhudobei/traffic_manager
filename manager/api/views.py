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
        sources = Source.objects.filter(remaining_traffic__gt=0, is_active=True)

        random_targets = []

        for source in sources:
            # get one random target from last five published
            target = random.choice(source.targets.order_by('-publish_time')[:5])

            # NOTE: Could move this operation to shared task
            target.traffic = F('traffic') + 1
            target.save()

            source.remaining_traffic = F('remaining_traffic') - 1
            source.save()

            random_targets.append(target.url)

        static_targets = StaticTarget.objects.filter(is_active=True)
        random_targets.extend(static_targets.values_list('url', flat=True))

        static_targets.update(traffic=F('traffic')+1)

        return Response(data=random_targets, status=status.HTTP_200_OK)
