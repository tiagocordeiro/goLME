import uuid

from django.contrib.auth.models import User
from django.db import models


def make_secret():
    return str(uuid.uuid4())


class TimeSerie(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(unique=True, max_length=50, blank=False, null=False)


class LondonMetalExchange(models.Model):
    date = models.DateField(primary_key=True)
    cobre = models.DecimalField(decimal_places=2, max_digits=20)
    zinco = models.DecimalField(decimal_places=2, max_digits=20)
    aluminio = models.DecimalField(decimal_places=2, max_digits=20)
    chumbo = models.DecimalField(decimal_places=2, max_digits=20)
    estanho = models.DecimalField(decimal_places=2, max_digits=20)
    niquel = models.DecimalField(decimal_places=2, max_digits=20)
    dolar = models.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        verbose_name_plural = "cotações"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profiles/')
    api_view = models.BooleanField("Habilitar API programática", default=False)
    api_secret_key = models.CharField(max_length=36, blank=True, null=True)
    site_url = models.URLField(max_length=200, blank=True, null=True)
    show_holidays = models.BooleanField("Exibir 'feriado'", default=False)

    class Meta:
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.user.get_username()

    def save(self, *args, **kwargs):
        if self.api_secret_key is None:
            self.api_secret_key = make_secret()
        super(Profile, self).save(*args, **kwargs)

class ApiRequestLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    profile = models.ForeignKey(
        "Profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="request_logs",
    )
    # Key literal apresentada na requisição (mesmo que inválida) — útil p/ abuso.
    api_key_used = models.CharField(max_length=64, blank=True, default="", db_index=True)
    url_name = models.CharField(max_length=64, blank=True, default="")
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=8)
    status_code = models.PositiveSmallIntegerField(default=0)
    ip = models.GenericIPAddressField(null=True, blank=True)
    # IP autoritativo da Cloudflare (nao falsificavel pelo cliente).
    cf_connecting_ip = models.GenericIPAddressField(null=True, blank=True)
    # Origem da requisicao (util para chamadas de navegador/iframe).
    referer = models.CharField(max_length=512, blank=True, default="")
    origin = models.CharField(max_length=512, blank=True, default="")
    user_agent = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "API request log"
        verbose_name_plural = "API request logs"
        indexes = [
            models.Index(fields=["profile", "timestamp"]),
            models.Index(fields=["api_key_used", "timestamp"]),
        ]

    def __str__(self):
        who = self.profile.user if self.profile_id else (self.api_key_used or "anon")
        return f"{self.timestamp:%Y-%m-%d %H:%M} {who} {self.path}"
