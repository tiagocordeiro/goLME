import logging

from .models import ApiRequestLog, Profile

logger = logging.getLogger(__name__)

# Só estas rotas (por url_name em core/urls.py) são consideradas "consumo de API".
# Assim não logamos estático, admin, nem as páginas HTML.
API_URL_NAMES = {
    "api",
    "api_periodo",
    "api_view_without_token",
    "api_periodo_without_token",
    "json_for_chart",
    "json_for_chart_by_period",
    "json_view",
    "json_view_data_in_root",
    "summary",
    "variations",
    "variations_with_period",
    "group_by_week_with_api",
    "group_by_week_iframe",
}


def _cf_ip(request):
    """IP que a Cloudflare enxergou. Ela sobrescreve este header, então o
    cliente não consegue forjar. Vazio se a requisição não passou pela CF."""
    return request.headers.get("CF-Connecting-IP", "").strip()


def _client_ip(request):
    """IP real do consumidor, por ordem de confiabilidade:
    1) CF-Connecting-IP (autoritativo atrás da Cloudflare, não falsificável)
    2) primeiro hop do X-Forwarded-For (cliente, mas falsificável)
    3) REMOTE_ADDR (o proxy/router mais próximo)"""
    cf = _cf_ip(request)
    if cf:
        return cf
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class ApiUsageLogMiddleware:
    """Registra cada requisição às rotas de API numa linha de ApiRequestLog.

    Não altera o comportamento das views — só observa a response e grava.
    Qualquer erro no logging é engolido (com log) pra nunca derrubar a request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._log(request, response)
        except Exception:  # nunca deixa o logging quebrar a resposta ao cliente
            logger.exception("Falha ao registrar ApiRequestLog")
        return response

    def _log(self, request, response):
        match = getattr(request, "resolver_match", None)
        if match is None or match.url_name not in API_URL_NAMES:
            return

        # A key pode vir no header Token (padrão novo) ou na URL (padrão legado).
        api_key = request.headers.get("Token") or match.kwargs.get("api_key") or ""

        profile = None
        if api_key:
            profile = Profile.objects.filter(api_secret_key=api_key).first()

        ApiRequestLog.objects.create(
            profile=profile,
            api_key_used=api_key[:64],
            url_name=match.url_name or "",
            path=request.path[:255],
            method=request.method,
            status_code=getattr(response, "status_code", 0),
            ip=_client_ip(request),
            cf_connecting_ip=_cf_ip(request) or None,
            referer=request.headers.get("Referer", "")[:512],
            origin=request.headers.get("Origin", "")[:512],
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
        )
