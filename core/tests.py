import sys
from datetime import date, timedelta
from decimal import Decimal

import django
from django.test import SimpleTestCase, TestCase

from core.facade import get_lme
from core.models import LondonMetalExchange


def criar_cotacoes(inicio: date, dias: int):
    """Cria `dias` cotações em datas corridas a partir de `inicio`."""
    registros = [
        LondonMetalExchange(
            date=inicio + timedelta(days=i),
            cobre=Decimal("1.00"),
            zinco=Decimal("1.00"),
            aluminio=Decimal("1.00"),
            chumbo=Decimal("1.00"),
            estanho=Decimal("1.00"),
            niquel=Decimal("1.00"),
            dolar=Decimal("5.00"),
        )
        for i in range(dias)
    ]
    LondonMetalExchange.objects.bulk_create(registros)


def fmt(d: date) -> str:
    return d.strftime("%d-%m-%Y")


class GetLmeLimitePeriodoTest(TestCase):
    """Issue #127: ao informar data inicial e final, a API deve retornar
    TODAS as cotações do período, não parar no limite padrão."""

    def test_periodo_longo_retorna_todas_as_cotacoes(self):
        inicio = date(2020, 1, 1)
        total = 150  # bem acima do limite padrão (40)
        criar_cotacoes(inicio, total)
        fim = inicio + timedelta(days=total - 1)

        resultado = get_lme(date_from=fmt(inicio), date_to=fmt(fim))

        self.assertEqual(
            len(resultado), total,
            "Um intervalo com 150 datas deveria retornar as 150; "
            "se parou em 40/100, o limite ainda esta cortando o periodo.",
        )

    def test_borda_inclusiva_conta_primeira_e_ultima_data(self):
        inicio = date(2021, 3, 1)
        criar_cotacoes(inicio, 60)
        fim = inicio + timedelta(days=59)

        resultado = list(get_lme(date_from=fmt(inicio), date_to=fmt(fim)))

        datas = {r.date for r in resultado}
        self.assertIn(inicio, datas, "A data inicial deve entrar no resultado.")
        self.assertIn(fim, datas, "A data final deve entrar no resultado (borda inclusiva).")
        self.assertEqual(len(resultado), 60)

    def test_limite_padrao_ainda_vale_sem_periodo_explicito(self):
        # Sem datas, o comportamento padrao (janela recente) nao deve estourar.
        criar_cotacoes(date(2022, 1, 1), 10)
        resultado = get_lme()
        self.assertLessEqual(len(resultado), 40)


class AppBoot(SimpleTestCase):
    """Protege o deploy na venv de producao: a app precisa inicializar mesmo
    sem o pacote `quandl` instalado (Quandl esta morto — Nasdaq Data Link)."""

    def test_app_inicializa_sem_quandl(self):
        # Nao deve levantar ImportError ao popular o registro de apps.
        django.setup()

        # E nenhum modulo carregado no boot pode ainda fazer `import quandl`
        # (se fizesse, estaria em sys.modules aqui).
        self.assertNotIn(
            "quandl",
            sys.modules,
            "Algum modulo importado no boot ainda faz `import quandl`.",
        )
