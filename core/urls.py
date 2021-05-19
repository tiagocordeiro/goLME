from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', views.api_view_with_token, name='api'),
    path('api/<date_from>/<date_to>', views.api_view_with_token, name='api_periodo'),
    path('api/v2/', views.api_view, name='api_view_without_token'),
    path('api/v2/<date_from>/<date_to>', views.api_view, name='api_periodo_without_token'),
    path('chart/', views.chart, name='chart'),
    path('chart/<date_from>/<date_to>', views.chart, name='chart_periodo'),
    path('grafico/', views.chart, name='grafico'),
    path('grafico/<str:api_key>/', views.chart, name='grafico'),
    path('grafico/<date_from>/<date_to>', views.chart, name='grafico_periodo'),
    path('periodo/<date_from>/<date_to>', views.periodo, name='periodo'),
    path('cotacao/', views.group_by_week, name='group_by_week'),
    path('cotacao/<str:api_key>/', views.group_by_week, name='group_by_week'),
    path('cotacao/<str:api_key>/json/', views.json_view, name='json_view'),
    path('cotacao/<str:api_key>/json/v2/', views.json_view_data_in_root, name='json_view_data_in_root'),
    path('about/', views.about, name='about'),
]
