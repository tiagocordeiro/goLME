from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin

from .models import Profile, TimeSerie, LondonMetalExchange


class TimeSerieAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


class LondonMetalExchangeAdmin(ImportExportModelAdmin):
    list_display = ("date", "cobre", "zinco", "aluminio", "chumbo", "estanho", "niquel", "dolar")
    search_fields = ("date",)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(TimeSerie, TimeSerieAdmin)
admin.site.register(LondonMetalExchange, LondonMetalExchangeAdmin)
