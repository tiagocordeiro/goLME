from django.db import models


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
