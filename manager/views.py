import datetime as dt

from django.shortcuts import render, get_object_or_404

from manager.models import Source


def source_statistic_view(request):
    source_name = request.GET.get('name')

    source = get_object_or_404(Source, name=source_name)
    dates = (
        source.targets
        .order_by('-created_at__date')
        .distinct('created_at__date')
        .values_list('created_at__date', flat=True)
    )

    try:
        selected_date = dt.date.fromisoformat(request.GET.get('date'))
    except (TypeError, ValueError):
        selected_date = dates[0] if dates else dt.date.today()

    targets = source.targets.filter(created_at__date=selected_date).order_by('-created_at')

    return render(request, template_name='manager/source_statistic.html', context={
        'source_name': source_name,
        'selected_date': selected_date,
        'targets': targets,
        'dates': dates,
    })
