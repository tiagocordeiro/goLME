import datetime
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from .facade import get_lme, json_builder, chart_builder, get_remote_addr
from .models import LondonMetalExchange, Profile


def index(request):
    lme = LondonMetalExchange.objects.all().order_by('-date')[:30]

    context = {
        'lme': lme,
    }
    return render(request, 'index.html', context)


def group_by_week(request):
    ip = get_remote_addr(request)
    print(ip)
    lme = LondonMetalExchange.objects.all().order_by('-date')[:50]

    context = {
        'lme': lme,
    }
    return render(request, 'group_by_week.html', context)


def api_view(request, date_from=None, date_to=None, limit=100):
    lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

    json_data = json_builder(lme_prices)

    data = {"results": json_data}
    return JsonResponse(data)


def api_view_with_token(request, date_from=None, date_to=None, limit=100):
    ip = get_remote_addr(request)

    try:
        secret_key = request.headers["Token"]

    except KeyError:
        response = JsonResponse({"status": "false", "message": "Token não informado"}, status=500)
        return response

    try:
        profile = Profile.objects.get(api_secret_key=secret_key)
        lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

        json_data = json_builder(lme_prices)

        data = {"results": json_data, "profile": f"{profile.user}", "remote_addr": f"{ip}"}
        response = JsonResponse(data)
        return response

    except Profile.DoesNotExist:
        response = JsonResponse({"status": "false", "message": "Token inválido"}, status=500)
        return response


@xframe_options_exempt
def chart(request, date_from=None, date_to=None, chart_id='lme', chart_type='line', chart_height=350, api_key=None):
    ip = get_remote_addr(request)
    origin = request.META.get('REMOTE_ADDR')
    if api_key:
        try:
            profile = Profile.objects.get(api_secret_key=api_key)
            print(ip)
            print(origin)
            print(profile.site_url)
        except Profile.DoesNotExist:
            return render(request, 'ops.html')
    else:
        profile = None

    context = chart_builder(date_from, date_to, chart_id, chart_type, chart_height)
    context["ip"] = ip
    context["token"] = api_key
    context["profile"] = profile
    context["origin"] = origin

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
