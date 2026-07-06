"""Pre-aquece o cache dos graficos mais pedidos.

O endpoint /chart/json/<date_from>/<date_to> deixa o plugin WP escolher qualquer
mes (seletor de 30+ meses). Cada mes frio recomputa pandas (~11-14s) e estoura o
timeout do plugin. Aqui aquecemos o grafico "atual" + os ultimos 12 meses para
que o seletor responda instantaneo.

So funciona de verdade com cache COMPARTILHADO (Redis): o scheduler escreve no
cache que os web dynos leem. Com LocMemCache o aquecimento fica preso no
processo que rodou o command (util so em dev/testes).
"""
import calendar

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
from django.utils import timezone

from core.facade import json_chart_builder_cached

# CRITICO: a VIEW json_for_chart passa chart_id='LME' (nao 'chart_LME', que e o
# default do facade). Precisamos aquecer com o MESMO chart_id, senao a chave
# aquecida nao bate com a que o cliente pede.
CHART_ID = 'LME'
CHART_TYPE = 'line'
CHART_HEIGHT = 350
MESES = 12


def preheat_cache():
    """Aquece o grafico atual + os ultimos 12 meses. Retorna quantos intervalos
    foram aquecidos (inclui o grafico atual).

    Nao remonta a chave de cache na mao: apenas CHAMA json_chart_builder_cached,
    que ja popula a chave certa seja qual for o esquema.
    """
    aquecidos = 0

    # Grafico "atual" (sem datas) -> mesma chamada que a view faz sem intervalo.
    json_chart_builder_cached(None, None, CHART_ID, CHART_TYPE, CHART_HEIGHT)
    aquecidos += 1

    hoje = timezone.localdate()
    for i in range(MESES):
        alvo = hoje - relativedelta(months=i)
        ultimo_dia = calendar.monthrange(alvo.year, alvo.month)[1]
        date_from = f"01-{alvo.month:02d}-{alvo.year}"
        date_to = f"{ultimo_dia:02d}-{alvo.month:02d}-{alvo.year}"
        json_chart_builder_cached(date_from, date_to, CHART_ID, CHART_TYPE, CHART_HEIGHT)
        aquecidos += 1

    return aquecidos


class Command(BaseCommand):
    help = 'Pre-aquece o cache do grafico atual e dos ultimos 12 meses.'

    def handle(self, *args, **options):
        aquecidos = preheat_cache()
        self.stdout.write(self.style.SUCCESS(
            f"Cache aquecido: {aquecidos} intervalos "
            f"(grafico atual + ultimos {MESES} meses)."
        ))
