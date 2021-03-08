import datetime
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

from .facade import get_lme, get_last_five_weeks, get_last, json_builder, chart_builder
from .models import LondonMetalExchange


def index(request):
    lme = LondonMetalExchange.objects.all().order_by('-date')[:30]

    context = {
        'lme': lme,
    }
    return render(request, 'index.html', context)


def group_by_week(request):
    lme = LondonMetalExchange.objects.all().order_by('-date')[:50]

    context = {
        'lme': lme,
    }
    return render(request, 'group_by_week.html', context)


def api_view(request, date_from=get_last_five_weeks(), date_to=get_last(), limit=100):
    lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

    json_data = json_builder(lme_prices)

    data = {"results": json_data}
    return JsonResponse(data)


def chart(request, date_from=get_last_five_weeks(), date_to=get_last(),
          chart_id='chart_LME', chart_type='line', chart_height=350):
    context = chart_builder(date_from, date_to, chart_id, chart_type, chart_height)

    if request.path.split('/')[1] == 'grafico':
        return render(request, 'chart.html', context)

    return render(request, 'with_chart.html', context)


def periodo(request, date_from, date_to):
    date_from = datetime.strptime(date_from, '%d-%m-%Y')
    date_to = datetime.strptime(date_to, '%d-%m-%Y')
    lme = LondonMetalExchange.objects.filter(date__range=(date_from, date_to))

    context = {
        'lme': lme,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'index.html', context)
