from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd
import holidays
from django.db.models import Avg

from .models import LondonMetalExchange


def get_last():
    try:
        last = LondonMetalExchange.objects.values('date').last()
        return str(datetime.strftime(last['date'] + timedelta(days=1), '%d-%m-%Y'))
    except TypeError:
        return str(datetime.strftime(datetime.today(), '%d-%m-%Y'))


def get_last_thirty_days():
    last = get_last()
    first = datetime.strptime(last, '%d-%m-%Y') - timedelta(days=30)
    return str(datetime.strftime(first, '%d-%m-%Y'))


def get_last_five_weeks():
    last = get_last()
    first = datetime.strptime(last, '%d-%m-%Y') - timedelta(weeks=5)
    return str(datetime.strftime(first, '%d-%m-%Y'))


def get_lme(date_from=None, date_to=None, limit=40):
    if date_from is None:
        date_from = get_last_five_weeks()
    else:
        date_from = date_from
    if date_to is None:
        date_to = get_last()
    else:
        date_to = date_to

    date_from = datetime.strptime(date_from, '%d-%m-%Y')
    date_to = datetime.strptime(date_to, '%d-%m-%Y')
    lme = LondonMetalExchange.objects.filter(date__range=(date_from, date_to)).order_by('date')[:limit]
    return lme


def json_builder(lme_prices):
    itens_list = []
    for item in lme_prices:
        itens_list.append(
            {
                "data": item.date,
                "cobre": item.cobre,
                "zinco": item.zinco,
                "aluminio": item.aluminio,
                "chumbo": item.chumbo,
                "estanho": item.estanho,
                "niquel": item.niquel,
                "dolar": item.dolar
            }
        )
    return itens_list


def chart_builder(date_from=None, date_to=None, chart_id='chart_LME', chart_type='line', chart_height=350):
    if date_from is None:
        date_from = get_last_five_weeks()
    else:
        date_from = date_from
    if date_to is None:
        date_to = get_last()
    else:
        date_to = date_to

    date_to = datetime.strptime(date_to, '%d-%m-%Y')
    date_from = datetime.strptime(date_from, '%d-%m-%Y')

    lme = LondonMetalExchange.objects.all().order_by('-date').filter(date__range=(date_from, date_to))

    lme_last = LondonMetalExchange.objects.values('date').last()

    lme_periodo = LondonMetalExchange.objects.filter(date__range=(date_from, date_to)).order_by('date')

    df = pd.DataFrame(
        list(lme_periodo.values('date', 'cobre', 'zinco', 'aluminio',
                                'chumbo', 'estanho', 'niquel', 'dolar', )))

    df['date'] = pd.to_datetime(df['date'], utc=True)

    df = df.set_index(df['date'])

    df = df.drop('date', axis=1)

    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    cobre = [float(item) for item in list(df['cobre'])]
    zinco = [float(item) for item in list(df['zinco'])]
    aluminio = [float(item) for item in list(df['aluminio'])]
    chumbo = [float(item) for item in list(df['chumbo'])]
    estanho = [float(item) for item in list(df['estanho'])]
    niquel = [float(item) for item in list(df['niquel'])]
    dolar = [float(item) for item in list(df['dolar'])]
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chart_id, "type": chart_type,
             "height": chart_height}

    series = [{"name": 'Cobre', "data": cobre},
              {"name": 'Zinco', "data": zinco},
              {"name": 'Alumínio', "data": aluminio},
              {"name": 'Chumbo', "data": chumbo},
              {"name": 'Estanho', "data": estanho},
              {"name": 'Níquel', "data": niquel},
              {"name": 'Dolar', "data": dolar}
              ]

    title = {"text": 'Cotação LME'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    context = {
        'lme': lme,
        'xAxis': xAxis,
        'yAxis': yAxis,
        'series': series,
        'title': title,
        'chart': chart,
        'chart_id': chart_id,
        'lme_last': lme_last['date'],
        'date_to': date_to,
        'date_from': date_from,
        'lme_periodo': lme_periodo,
    }

    return context


def json_chart_builder(date_from=None, date_to=None, chart_id='chart_LME', chart_type='line', chart_height=350):
    if date_from is None:
        date_from = get_last_five_weeks()
    else:
        date_from = date_from
    if date_to is None:
        date_to = get_last()
    else:
        date_to = date_to

    date_to = datetime.strptime(date_to, '%d-%m-%Y')
    date_from = datetime.strptime(date_from, '%d-%m-%Y')

    lme = LondonMetalExchange.objects.all().order_by('-date').filter(date__range=(date_from, date_to))

    lme_last = LondonMetalExchange.objects.values('date').last()

    lme_periodo = LondonMetalExchange.objects.filter(date__range=(date_from, date_to)).order_by('date')

    df = pd.DataFrame(
        list(lme_periodo.values('date', 'cobre', 'zinco', 'aluminio',
                                'chumbo', 'estanho', 'niquel', 'dolar', )))

    df['date'] = pd.to_datetime(df['date'], utc=True)

    df = df.set_index(df['date'])

    df = df.drop('date', axis=1)

    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    cobre = [float(item) for item in list(df['cobre'])]
    zinco = [float(item) for item in list(df['zinco'])]
    aluminio = [float(item) for item in list(df['aluminio'])]
    chumbo = [float(item) for item in list(df['chumbo'])]
    estanho = [float(item) for item in list(df['estanho'])]
    niquel = [float(item) for item in list(df['niquel'])]
    dolar = [float(item) for item in list(df['dolar'])]
    data = list(df.index.strftime('%d/%m/%y'))

    chart = {"renderTo": chart_id, "type": chart_type,
             "height": chart_height}

    series = [{"name": 'Cobre', "data": cobre},
              {"name": 'Zinco', "data": zinco},
              {"name": 'Alumínio', "data": aluminio},
              {"name": 'Chumbo', "data": chumbo},
              {"name": 'Estanho', "data": estanho},
              {"name": 'Níquel', "data": niquel},
              {"name": 'Dolar', "data": dolar}
              ]

    title = {"text": 'Cotação LME'}
    xAxis = {"categories": data, "crosshair": 'true'}
    yAxis = {"title": {"text": 'Valor'}}

    context = {
        'xAxis': xAxis,
        'yAxis': yAxis,
        'series': series,
        'title': title,
        'chart': chart,
        'chart_id': chart_id,
    }

    return context


def get_remote_addr(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_lme_avg(lme):
    media_cobre = lme.aggregate(Avg('cobre'))
    media_zinco = lme.aggregate(Avg('zinco'))
    media_aluminio = lme.aggregate(Avg('aluminio'))
    media_chumbo = lme.aggregate(Avg('chumbo'))
    media_estanho = lme.aggregate(Avg('estanho'))
    media_niquel = lme.aggregate(Avg('niquel'))
    media_dolar = lme.aggregate(Avg('dolar'))
    return {
        'media_cobre': media_cobre,
        'media_zinco': media_zinco,
        'media_aluminio': media_aluminio,
        'media_chumbo': media_chumbo,
        'media_estanho': media_estanho,
        'media_niquel': media_niquel,
        'media_dolar': media_dolar,
    }


def treats_holidays(lme):
    holidays_lme = holidays.UK()
    holidays_br = holidays.BR()

    # dropa funeral da rainha
    holidays_lme.pop("2022-09-19")

    for item in lme:
        if item.date in holidays_lme:
            item.cobre = 'feriado'
            item.zinco = 'feriado'
            item.aluminio = 'feriado'
            item.chumbo = 'feriado'
            item.estanho = 'feriado'
            item.niquel = 'feriado'

        if item.date in holidays_br:
            item.dolar = 'feriado'

    return lme


def variations(date_from=None, date_to=None):
    # Inicialização das datas
    date_from = date_from or get_last_five_weeks()
    date_to = date_to or get_last()

    # Conversão de string para datetime
    date_to = datetime.strptime(date_to, '%d-%m-%Y')
    date_from = datetime.strptime(date_from, '%d-%m-%Y')

    # Busca os dados para o período
    lme_periodo = LondonMetalExchange.objects.filter(date__range=(date_from, date_to)).order_by('date')

    # Calcula o número de semanas
    days = abs(date_to - date_from).days
    weeks = days // 7

    # Lista de metais para processamento
    metais = ['cobre', 'zinco', 'aluminio', 'chumbo', 'estanho', 'niquel', 'dolar']
    nomes_metais = ['Cobre', 'Zinco', 'Alumínio', 'Chumbo', 'Estanho', 'Níquel', 'Dolar']

    # Estruturas de dados para armazenar resultados
    lista_semanas = []
    lista_semanas_data = []
    valores_semanais = {metal: [] for metal in metais}  # Dicionário para valores semanais

    # Função auxiliar para arredondar com segurança
    def safe_round(value):
        return 0 if value is None else round(value, 2)

    # Cálculo das médias semanais
    data_base = date_to
    for _ in range(weeks):
        # Identifica a semana
        semana_label = f"semana {data_base.strftime('%W')}/{data_base.year}"
        lista_semanas_data.append(semana_label)

        # Filtra dados da semana
        valores_semana = lme_periodo.filter(date__week=data_base.strftime('%W'), date__year=data_base.year)

        # Calcula médias e armazena
        semana_dados = {}

        for metal in metais:
            media = valores_semana.aggregate(Avg(metal))
            valor = safe_round(media[f'{metal}__avg'])
            semana_dados[metal] = valor
            valores_semanais[metal].append(valor)

        lista_semanas.append({semana_label: semana_dados})
        data_base = data_base - timedelta(weeks=1)

    # Estruturas de dados para médias mensais
    lista_meses = []
    lista_meses_data = []
    valores_mensais = {metal: [] for metal in metais}  # Dicionário para valores mensais

    # Verifica se o mês atual tem dados
    mes_base = date_to
    valores_teste = LondonMetalExchange.objects.filter(
        date__month=mes_base.strftime('%m'),
        date__year=mes_base.year
    ).order_by('date')

    if not valores_teste:
        mes_base = mes_base - relativedelta(months=1)

    # Cálculo das médias mensais (12 meses)
    for _ in range(12):
        # Identifica o mês
        mes_label = f"{mes_base.strftime('%m')}/{mes_base.year}"
        lista_meses_data.append(mes_label)

        # Filtra dados do mês
        valores_mes = LondonMetalExchange.objects.filter(
            date__month=mes_base.strftime('%m'),
            date__year=mes_base.year
        ).order_by('date')

        # Calcula médias e armazena
        mes_dados = {}

        for metal in metais:
            media = valores_mes.aggregate(Avg(metal))
            valor = safe_round(media[f'{metal}__avg'])
            mes_dados[metal] = valor
            valores_mensais[metal].append(valor)

        lista_meses.append({mes_label: mes_dados})
        mes_base = mes_base - relativedelta(months=1)

    # Cria séries para gráficos
    series_semanal = []
    series_mensal = []

    for i, metal in enumerate(metais):
        series_semanal.append({"name": nomes_metais[i], "data": valores_semanais[metal]})
        series_mensal.append({"name": nomes_metais[i], "data": valores_mensais[metal]})

    # Configura títulos e eixos
    semanal_title = {"text": 'Variação semanal LME'}
    semanal_xaxis = {"categories": lista_semanas_data, "crosshair": 'true'}
    semanal_yaxis = {"title": {"text": 'Valor'}}

    mensal_title = {"text": 'Variação mensal LME'}
    mensal_xaxis = {"categories": lista_meses_data, "crosshair": 'true'}
    mensal_yaxis = {"title": {"text": 'Valor'}}

    # Monta o resultado final
    context = {
        "mensal": {
            "xAxis": mensal_xaxis,
            "yAxis": mensal_yaxis,
            "series": series_mensal,
            "title": mensal_title
        },
        "semanal": {
            "xAxis": semanal_xaxis,
            "yAxis": semanal_yaxis,
            "series": series_semanal,
            "title": semanal_title
        },
        "semanas": lista_semanas,
        "meses": lista_meses,
    }

    return context
