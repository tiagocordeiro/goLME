from datetime import date, timedelta
from time import sleep

import pandas as pd
import quandl
import requests
from django.core.management import BaseCommand

from core.models import LondonMetalExchange, TimeSerie


def update_metal_exchange():
    timeseries = TimeSerie.objects.all()
    lista = []
    colunas = []
    for serie in timeseries:
        lista.append(serie.code)
        colunas.append(serie.name)

    todo_periodo = quandl.get(lista,
                              start_date='2012-01-03',
                              returns='pandas')

    colunas.insert(0, 'date')

    df = pd.DataFrame(todo_periodo)
    df.reset_index(level=0, inplace=True)

    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)

    df.columns = colunas

    cotacoes_dict = []
    for cotacao in df.itertuples():
        cotacao = LondonMetalExchange(date=cotacao[1],
                                      cobre=cotacao[2],
                                      zinco=cotacao[3],
                                      aluminio=cotacao[4],
                                      chumbo=cotacao[5],
                                      estanho=cotacao[6],
                                      niquel=cotacao[7],
                                      dolar=cotacao[8])
        cotacoes_dict.append(cotacao)

    last_in_dict = cotacoes_dict[-1].date

    try:
        last_in_db = LondonMetalExchange.objects.last().date
        if last_in_db < last_in_dict:
            print(f"No banco: {last_in_db}, mais recente: {last_in_dict}")
            LondonMetalExchange.objects.all().delete()
            LondonMetalExchange.objects.bulk_create(cotacoes_dict)
            print("Cotações atualizadas")

    except AttributeError:
        print(f"No banco: vazio, mais recente: {last_in_dict}")
        LondonMetalExchange.objects.bulk_create(cotacoes_dict)
        print("Cotações adicionadas")


def datetime_to_string(value, format='%Y-%m-%d %H:%M:%S'):
    '''Transforma datetime em string no formato %Y-%m-%d %H:%M:%S.'''
    return value.strftime(format)


def update_dolar_exchange(start_date='01-04-2021', end_date=None):  # 01-03-2012
    '''Inserir data no formato mm-dd-yyyy'''

    # Verifica o intervalo de datas
    # Se for mais de um ano, faz um loop com uma requisição por ano.

    start_day = start_date[3:5]
    start_month = start_date[:2]
    start_year = int(start_date[-4:])
    end_year = int(end_date[-4:])

    for y in range(start_year, end_year + 1):
        sleep(3)  # sleepzinho pra dar uma folga pra API.

        # Corrige os anos seguintes para pegar desde o dia primeiro de Janeiro de cada ano.
        if y != start_year:
            start_day = '01'
            start_month = '01'

        start_date_str = '-'.join((start_month, start_day, str(y)))
        end_date_str = '-'.join((start_month, start_day, str(y + 1)))

        url = 'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/'
        url += 'CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)'
        url += f'?@dataInicial=%27{start_date_str}%27&@dataFinalCotacao=%27{end_date_str}%27&$top=400&$format=json'

        response = requests.get(url)
        result = response.json().get('value')
        if result:
            '''
            Gera uma list comprehension convertendo o datetime em date
            e gerando uma tupla com data e cotacaoVenda.
            Ex:
            [
                ('2021-07-01', 5.0055),
                ('2021-07-02', 5.0293),
                ('2021-07-05', 5.0749)
            ]
            '''
            data_indexed = [
                (item['dataHoraCotacao'].split()[0], item['cotacaoVenda'])
                for item in result
            ]
            for item in data_indexed:
                date, dolar = item
                obj = LondonMetalExchange.objects.filter(date=date).first()
                if obj:
                    obj.dolar = dolar
                    obj.save()


class Command(BaseCommand):
    help = '''Atualiza cotações no banco de dados'''

    def add_arguments(self, parser):
        parser.add_argument(
            '--start_date', '-sd',
            dest='start_date',
            default=None,
            help='Insira a data no formato m-d-YYYY.'
        )

    def handle(self, *args, **options):
        start_date = options.get('start_date')

        update_metal_exchange()

        if start_date:
            one_year_ago_str = start_date
        else:
            one_year_ago = date.today() - timedelta(days=360)
            one_year_ago_str = datetime_to_string(one_year_ago, format='%m-%d-%Y')  # noqa E501

        today = datetime_to_string(date.today(), format='%m-%d-%Y')

        update_dolar_exchange(start_date=one_year_ago_str, end_date=today)
