import datetime

from django.core.cache import cache
from django.core.management import BaseCommand

from core.models import LondonMetalExchange
from core.new_data import get_data_exchange


def update_metal_exchange():
    items = get_data_exchange()

    created = 0
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
            created += 1

    return created


class Command(BaseCommand):
    help = '''Atualiza cotações lme no banco de dados'''

    def handle(self, *args, **options):
        created = update_metal_exchange()

        if created > 0:
            # Invalida o cache das cotacoes ao entrar dado novo.
            # OBS: com LocMemCache o cache e por-processo, entao cache.clear()
            # so limpa o cache deste processo (o dyno que roda o cron). O frescor
            # real nos web dynos vem do TTL (LME_CACHE_TTL). Se um dia trocar o
            # backend para Redis, este clear passa a valer cross-dyno.
            cache.clear()
