import uuid
import datetime as dt

from django.http import HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils import translation

from manager.models import Source


@translation.override('uk-ua')
def source_statistic_view(request, token):
    date = request.GET.get('date')

    try:
        token = uuid.UUID(token)
    except (TypeError, ValueError):
        return HttpResponseNotFound()

    source = get_object_or_404(Source, statistic_view_token=token)
    dates = (
        source.targets
        .order_by('-publish_time__date')
        .distinct('publish_time__date')
        .values_list('publish_time__date', flat=True)
    )

    try:
        selected_date = dt.date.fromisoformat(date)
        assert source.targets.filter(publish_time__date=selected_date).first() is not None

    except (TypeError, ValueError, AssertionError):
        selected_date = dates[0] if dates else dt.date.today()

    targets = source.targets.filter(publish_time__date=selected_date).order_by('-publish_time')

    return render(request, template_name='manager/source_statistic.html', context={
        'source_name': source.name,
        'selected_date': selected_date,
        'targets': targets,
        'dates': dates,
    })
