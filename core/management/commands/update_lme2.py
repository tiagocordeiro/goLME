import datetime

from django.core.cache import cache
from django.core.management import BaseCommand

from core.management.commands.preheat_cache import preheat_cache
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
            # Entrou dado novo: invalida o cache e ja re-aquece no mesmo passo.
            # Com Redis (cache compartilhado) o cache.clear() vale cross-dyno e
            # o pre-aquecimento escreve as chaves que os web dynos vao ler, entao
            # o seletor de meses responde instantaneo logo apos o update.
            cache.clear()
            aquecidos = preheat_cache()
            self.stdout.write(self.style.SUCCESS(
                f"Cache invalidado e reaquecido: {aquecidos} intervalos."
            ))
