import datetime
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt

from .facade import get_lme, json_builder, chart_builder, get_remote_addr, get_lme_avg, json_chart_builder
from .forms import ProfileForm
from .models import LondonMetalExchange, Profile


def index(request, date_from=None, date_to=None, chart_id='LME', chart_type='line', chart_height=350):
    context = chart_builder(date_from, date_to, chart_id, chart_type, chart_height)

    return render(request, 'index.html', context)


def app_view(request, date_from=None, date_to=None, chart_id='LME', chart_type='line', chart_height=350):
    context = chart_builder(date_from, date_to, chart_id, chart_type, chart_height)

    return render(request, 'app.html', context)


def group_by_week(request, api_key=None):
    lme = LondonMetalExchange.objects.all().order_by('-date')[:50]
    media_periodo = get_lme_avg(lme)

    if api_key:
        try:
            profile = Profile.objects.get(api_secret_key=api_key)
        except Profile.DoesNotExist:
            return render(request, 'ops.html')
    else:
        profile = None

    context = {
        'lme': lme,
        'profile': profile,
        'media_periodo': media_periodo,
    }
    return render(request, 'group_by_week.html', context)


@login_required
def api_view(request, date_from=None, date_to=None, limit=100):
    lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

    json_data = json_builder(lme_prices)

    data = {"results": json_data}
    return JsonResponse(data)


def json_view(request, date_from=None, date_to=None, limit=100, api_key=None):
    if api_key:
        try:
            Profile.objects.get(api_secret_key=api_key)
        except Profile.DoesNotExist:
            return render(request, 'ops.html')

    lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

    json_data = json_builder(lme_prices)

    data = {"results": json_data}
    return JsonResponse(data)


def summary(request, date_from=None, date_to=None, limit=100):
    lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

    json_data = json_builder(lme_prices)

    data = {"result": json_data[-1]}
    return JsonResponse(data)


def json_view_data_in_root(request, date_from=None, date_to=None, limit=100, api_key=None):
    if api_key:
        try:
            Profile.objects.get(api_secret_key=api_key)
        except Profile.DoesNotExist:
            return render(request, 'ops.html')

    lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

    json_data = json_builder(lme_prices)

    return JsonResponse(json_data, safe=False)


def json_for_chart(request, date_from=None, date_to=None, chart_id='LME', chart_type='line', chart_height=350):
    try:
        secret_key = request.headers["Token"]

    except KeyError:
        response = JsonResponse({"status": "false", "message": "Token não informado"}, status=500)
        return response

    try:
        Profile.objects.get(api_secret_key=secret_key)
        chart_data = json_chart_builder(date_from, date_to, chart_id, chart_type, chart_height)

        response = JsonResponse(chart_data)
        return response

    except Profile.DoesNotExist:
        response = JsonResponse({"status": "false", "message": "Token inválido"}, status=500)
        return response


def api_view_with_token(request, date_from=None, date_to=None, limit=100):
    ip = get_remote_addr(request)
    origin = request.META.get('REMOTE_ADDR')

    try:
        secret_key = request.headers["Token"]

    except KeyError:
        response = JsonResponse({"status": "false", "message": "Token não informado"}, status=500)
        return response

    try:
        profile = Profile.objects.get(api_secret_key=secret_key)
        lme_prices = get_lme(date_from=date_from, date_to=date_to, limit=limit)

        json_data = json_builder(lme_prices)

        data = {"results": json_data,
                "profile": f"{profile.user}",
                "remote_addr": f"{ip}",
                "origin": f"{origin}"}

        response = JsonResponse(data)
        return response

    except Profile.DoesNotExist:
        response = JsonResponse({"status": "false", "message": "Token inválido"}, status=500)
        return response


@xframe_options_exempt
def chart(request, date_from=None, date_to=None, chart_id='LME', chart_type='line', chart_height=350, api_key=None):
    ip = get_remote_addr(request)
    origin = request.META.get('REMOTE_ADDR')
    if api_key:
        try:
            profile = Profile.objects.get(api_secret_key=api_key)
        except Profile.DoesNotExist:
            return render(request, 'ops.html')
    else:
        profile = None

    data_inicio = request.GET.get('data-inicio', False)
    data_final = request.GET.get('data-final', False)

    if data_inicio and data_final:
        data_inicio = '-'.join(data_inicio.split('-')[::-1])
        data_final = '-'.join(data_final.split('-')[::-1])
        url_with_dates = f'/chart/{data_inicio}/{data_final}'

        return redirect(url_with_dates)

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


def about(request):
    return render(request, 'about.html')


def docs(request):
    return render(request, 'docs.html')


@login_required
def profile_update(request):
    try:
        usuario = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        usuario = None

    user = User.objects.get(username=request.user)

    profile_inline_formset = inlineformset_factory(User, Profile, fields=('avatar',))

    if request.method == 'POST':
        form = ProfileForm(data=request.POST, instance=request.user)
        formset = profile_inline_formset(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            perfil = form.save(commit=False)
            formset = profile_inline_formset(request.POST, request.FILES, instance=perfil)

            if formset.is_valid():
                perfil.save()
                formset.save()
                return redirect('profile_update')

    else:
        form = ProfileForm(instance=request.user)
        formset = profile_inline_formset(instance=request.user)

    return render(request, 'profile_update.html', {'form': form,
                                                   'formset': formset,
                                                   'usuario': usuario,
                                                   'user': user, })
