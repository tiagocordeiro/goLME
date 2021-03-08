from django.contrib import admin

from .models import TimeSerie


class TimeSerieAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


admin.site.register(TimeSerie, TimeSerieAdmin)
