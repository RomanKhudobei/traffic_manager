import random
import json

from django.db.models import Sum, F
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from manager.models import Target, Source


class GetRandomTargetsApiView(APIView):
    # TODO: implement auth

    def get(self, request):

        source_ids = Target.objects.values('source').annotate(
            traffic_count=Sum('traffic')
        ).filter(
            traffic_count__lt=F('source__limit')
        ).values_list(
            'source',
            flat=True
        )

        random_targets = []

        for source_id in source_ids:
            source = Source.objects.get(id=source_id)

            target = random.choice(source.targets.order_by('-publish_time')[:5])    # TODO: move limit number to the config
            target.traffic = F('traffic') + 1
            target.save()

            random_targets.append(target.url)

        return Response(data=json.dumps(random_targets), status=status.HTTP_200_OK)
