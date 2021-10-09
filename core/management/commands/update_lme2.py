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
            # Se existir LondonMetalExchange, então atualiza os dados.
            for key, value in values.items():
                setattr(obj, key, value)
            obj.save()
        else:
            # Senão cria um novo.
            LondonMetalExchange.objects.create(**values)


class Command(BaseCommand):
    help = '''Atualiza cotações lme no banco de dados'''

    def handle(self, *args, **options):
        update_metal_exchange()
