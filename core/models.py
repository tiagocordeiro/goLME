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

    class Meta:
        verbose_name_plural = "Profiles"

    def save(self, *args, **kwargs):
        if self.api_secret_key is None:
            self.api_secret_key = make_secret()
        super(Profile, self).save(*args, **kwargs)
