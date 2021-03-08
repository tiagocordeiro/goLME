from datetime import datetime, timedelta

import pandas as pd

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


def get_lme(date_from=get_last_five_weeks(), date_to=get_last(), limit=40):
    date_from = datetime.strptime(date_from, '%d-%m-%Y')
    date_to = datetime.strptime(date_to, '%d-%m-%Y')
    lme = LondonMetalExchange.objects.filter(date__range=(date_from, date_to))[:limit]
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


def chart_builder(date_from=get_last_five_weeks(), date_to=get_last(),
                  chart_id='chart_LME', chart_type='line', chart_height=350):
    date_to = datetime.strptime(date_to, '%d-%m-%Y')
    date_from = datetime.strptime(date_from, '%d-%m-%Y')

    lme = LondonMetalExchange.objects.all().order_by('-date').filter(date__range=(date_from, date_to))

    lme_last = LondonMetalExchange.objects.values('date').last()

    lme_periodo = LondonMetalExchange.objects.filter(date__range=(date_from, date_to))

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
