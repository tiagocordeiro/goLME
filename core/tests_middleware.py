from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import resolve

from core.middleware import ApiUsageLogMiddleware
from core.models import ApiRequestLog, Profile


def make_middleware(status=200):
    def get_response(request):
        return HttpResponse(status=status)
    return ApiUsageLogMiddleware(get_response)


@override_settings(ROOT_URLCONF="core.urls")
class ApiUsageLogMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username="cliente")
        self.profile = Profile.objects.create(user=self.user, api_secret_key="KEY-VALIDA")

    def _call(self, path, status=200, **extra):
        request = self.factory.get(path, **extra)
        request.resolver_match = resolve(path)
        return make_middleware(status)(request)

    def test_rota_de_api_gera_log(self):
        self._call("/summary/")
        self.assertEqual(ApiRequestLog.objects.count(), 1)
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.url_name, "summary")
        self.assertEqual(log.status_code, 200)
        self.assertEqual(log.method, "GET")

    def test_rota_nao_api_nao_gera_log(self):
        # /about/ existe no core.urls, mas nao e rota de API
        self._call("/about/")
        self.assertEqual(ApiRequestLog.objects.count(), 0)

    def test_key_na_url_liga_ao_profile(self):
        self._call("/cotacao/KEY-VALIDA/json/")
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.profile, self.profile)
        self.assertEqual(log.api_key_used, "KEY-VALIDA")
        self.assertEqual(log.url_name, "json_view")

    def test_key_no_header_liga_ao_profile(self):
        self._call("/summary/", HTTP_TOKEN="KEY-VALIDA")
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.profile, self.profile)
        self.assertEqual(log.api_key_used, "KEY-VALIDA")

    def test_key_invalida_registra_sem_profile(self):
        self._call("/cotacao/NAO-EXISTE/json/")
        log = ApiRequestLog.objects.get()
        self.assertIsNone(log.profile)
        self.assertEqual(log.api_key_used, "NAO-EXISTE")

    def test_acesso_anonimo_sem_key_registra_sem_profile(self):
        self._call("/summary/")
        log = ApiRequestLog.objects.get()
        self.assertIsNone(log.profile)
        self.assertEqual(log.api_key_used, "")

    def test_ip_vem_do_primeiro_hop_do_xff(self):
        self._call("/summary/", HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.1")
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.ip, "1.2.3.4")

    def test_erro_no_log_nao_derruba_a_resposta(self):
        request = self.factory.get("/summary/")
        request.resolver_match = resolve("/summary/")
        with patch("core.middleware.ApiRequestLog.objects.create",
                   side_effect=Exception("boom")):
            response = make_middleware()(request)
        self.assertEqual(response.status_code, 200)  # cliente nao ve o erro
        self.assertEqual(ApiRequestLog.objects.count(), 0)


@override_settings(ROOT_URLCONF="core.urls")
class ApiUsageLogOrigemTest(TestCase):
    """Issue #131: IP autoritativo da Cloudflare (CF-Connecting-IP) e captura
    de Referer/Origin."""

    def setUp(self):
        self.factory = RequestFactory()

    def _call(self, path, **extra):
        request = self.factory.get(path, **extra)
        request.resolver_match = resolve(path)
        return make_middleware()(request)

    def test_cf_connecting_ip_tem_prioridade_sobre_xff(self):
        self._call("/summary/",
                   HTTP_CF_CONNECTING_IP="200.100.50.25",
                   HTTP_X_FORWARDED_FOR="10.0.0.9, 172.16.0.1")
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.ip, "200.100.50.25")
        self.assertEqual(log.cf_connecting_ip, "200.100.50.25")

    def test_xff_forjado_e_ignorado_quando_ha_cf(self):
        # Cliente tenta forjar o XFF; a CF anexa o IP real e preenche o header.
        self._call("/summary/",
                   HTTP_CF_CONNECTING_IP="200.100.50.25",
                   HTTP_X_FORWARDED_FOR="1.2.3.4")  # forjado
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.ip, "200.100.50.25")   # NAO usa o forjado
        self.assertNotEqual(log.ip, "1.2.3.4")

    def test_fallback_para_xff_sem_header_da_cloudflare(self):
        self._call("/summary/", HTTP_X_FORWARDED_FOR="8.8.8.8, 10.0.0.1")
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.ip, "8.8.8.8")
        self.assertIsNone(log.cf_connecting_ip)

    def test_referer_e_origin_sao_capturados(self):
        self._call("/summary/",
                   HTTP_REFERER="https://cliente.com.br/cotacoes",
                   HTTP_ORIGIN="https://cliente.com.br")
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.referer, "https://cliente.com.br/cotacoes")
        self.assertEqual(log.origin, "https://cliente.com.br")

    def test_sem_origem_campos_ficam_vazios(self):
        self._call("/summary/")
        log = ApiRequestLog.objects.get()
        self.assertEqual(log.referer, "")
        self.assertEqual(log.origin, "")
        self.assertIsNone(log.cf_connecting_ip)
