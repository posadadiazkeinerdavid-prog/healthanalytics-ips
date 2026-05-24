from django.urls import path
from .frontend_views import (
    login_page, dashboard_page, etl_page,
    analytics_page, ml_page, reports_page, pacientes_page
)

urlpatterns = [
    path('', dashboard_page, name='dashboard'),
    path('login/', login_page, name='login'),
    path('etl/', etl_page, name='etl'),
    path('analytics/', analytics_page, name='analytics'),
    path('ml/', ml_page, name='ml'),
    path('reportes/', reports_page, name='reports'),
    path('pacientes/', pacientes_page, name='pacientes'),
]
