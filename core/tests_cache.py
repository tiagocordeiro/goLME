"""Testes do cache da construcao das cotacoes (issue lentidao/H12).

Rodar com: DJANGO_SETTINGS_MODULE=golme.test_settings python manage.py test core

O objetivo e provar que os wrappers de core.facade cacheiam a CONSTRUCAO do
dado: a funcao pesada roda 1x por chave, chaves diferentes nao colidem e
cache.clear() forca o recomputo.
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

from django.core.cache import cache
from django.test import TestCase

from core import facade
from core.facade import (
    build_lme_json,
    json_chart_builder_cached,
    summary_data,
    variations_cached,
)
from core.models import LondonMetalExchange


def fmt(d: date) -> str:
    return d.strftime("%d-%m-%Y")


class CacheCotacoesTest(TestCase):
    def setUp(self):
        # Cada teste comeca com cache limpo e um seed determinístico.
        cache.clear()
        self.inicio = date(2020, 1, 1)
        registros = [
            LondonMetalExchange(
                date=self.inicio + timedelta(days=i),
                cobre=Decimal("1.00"),
                zinco=Decimal("1.00"),
                aluminio=Decimal("1.00"),
                chumbo=Decimal("1.00"),
                estanho=Decimal("1.00"),
                niquel=Decimal("1.00"),
                dolar=Decimal("5.00"),
            )
            for i in range(10)
        ]
        LondonMetalExchange.objects.bulk_create(registros)
        self.fim = self.inicio + timedelta(days=9)

    def test_build_lme_json_cacheia_e_nao_recomputa(self):
        # wraps=real: o spy conta as chamadas mas ainda executa a funcao real.
        with mock.patch.object(facade, "json_builder", wraps=facade.json_builder) as spy:
            r1 = build_lme_json(fmt(self.inicio), fmt(self.fim))
            r2 = build_lme_json(fmt(self.inicio), fmt(self.fim))

        self.assertEqual(spy.call_count, 1, "json_builder deveria rodar so 1x (2a chamada e cache hit).")
        self.assertEqual(r1, r2)

    def test_json_chart_builder_cached_cacheia_e_nao_recomputa(self):
        with mock.patch.object(facade, "json_chart_builder", wraps=facade.json_chart_builder) as spy:
            r1 = json_chart_builder_cached(fmt(self.inicio), fmt(self.fim))
            r2 = json_chart_builder_cached(fmt(self.inicio), fmt(self.fim))

        self.assertEqual(spy.call_count, 1, "json_chart_builder deveria rodar so 1x.")
        self.assertEqual(r1, r2)

    def test_summary_data_cacheia_e_nao_reconsulta(self):
        with mock.patch.object(
            LondonMetalExchange.objects, "last", wraps=LondonMetalExchange.objects.last
        ) as spy:
            r1 = summary_data()
            r2 = summary_data()

        self.assertEqual(spy.call_count, 1, "objects.last() deveria ser consultado so 1x.")
        self.assertEqual(r1, r2)

    def test_chaves_diferentes_nao_colidem(self):
        # Intervalos diferentes => chaves diferentes => recomputa cada um.
        meio = self.inicio + timedelta(days=4)
        with mock.patch.object(facade, "json_builder", wraps=facade.json_builder) as spy:
            build_lme_json(fmt(self.inicio), fmt(meio))
            build_lme_json(fmt(meio + timedelta(days=1)), fmt(self.fim))

        self.assertEqual(spy.call_count, 2, "Intervalos distintos nao devem compartilhar chave de cache.")

    def test_cache_clear_forca_recomputo(self):
        with mock.patch.object(facade, "json_builder", wraps=facade.json_builder) as spy:
            build_lme_json(fmt(self.inicio), fmt(self.fim))  # miss -> computa
            cache.clear()
            build_lme_json(fmt(self.inicio), fmt(self.fim))  # cache vazio -> recomputa

        self.assertEqual(spy.call_count, 2, "Apos cache.clear() a mesma chave deve recomputar.")

    def test_variations_cached_cacheia_e_nao_recomputa(self):
        with mock.patch.object(facade, "variations", wraps=facade.variations) as spy:
            r1 = variations_cached(fmt(self.inicio), fmt(self.fim))
            r2 = variations_cached(fmt(self.inicio), fmt(self.fim))

        self.assertEqual(spy.call_count, 1, "variations deveria rodar so 1x (2a chamada e cache hit).")
        self.assertEqual(r1, r2)

    def test_variations_cached_chaves_diferentes_nao_colidem(self):
        # Intervalos diferentes => chaves diferentes => recomputa cada um.
        meio = self.inicio + timedelta(days=4)
        with mock.patch.object(facade, "variations", wraps=facade.variations) as spy:
            variations_cached(fmt(self.inicio), fmt(meio))
            variations_cached(fmt(meio + timedelta(days=1)), fmt(self.fim))

        self.assertEqual(spy.call_count, 2, "Intervalos distintos nao devem compartilhar chave de cache.")
