import datetime

from django.core.management import BaseCommand

from core.models import LondonMetalExchange
from core.new_data import get_data_exchange


def update_metal_exchange():
    items = get_data_exchange()

    for item in items:
        values = dict(
            date=item['date'],
            cobre=item['cobre'],
            zinco=item['zinco'],
            aluminio=item['aluminio'],
            chumbo=item['chumbo'],
            estanho=item['estanho'],
            niquel=item['niquel'],
            dolar=item['dolar'],
        )
        obj = LondonMetalExchange.objects.filter(date=item['date']).first()
        if obj:
            # Se existir LondonMetalExchange, então não atualiza os dados.
            pass
        elif values['date'].month == 12 and datetime.date.today().month == 1:
            # Se for cotação de dezembro do ano anterior, então ignora.
            pass
        else:
            # Senão cria um novo.
            LondonMetalExchange.objects.create(**values)


class Command(BaseCommand):
    help = '''Atualiza cotações lme no banco de dados'''

    def handle(self, *args, **options):
        update_metal_exchange()
