import pandas as pd
import quandl
from django.core.management import BaseCommand

from core.models import TimeSerie, LondonMetalExchange


class Command(BaseCommand):
    help = '''Atualiza cotações no banco de dados'''

    def handle(self, *args, **options):
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
