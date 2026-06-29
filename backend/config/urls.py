"""
HealthAnalytics IPS - Main URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="HealthAnalytics IPS API",
        default_version='v1',
        description="Plataforma Inteligente de Analítica Clínica para Detección de Riesgo Médico",
        contact=openapi.Contact(email="admin@healthanalytics.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Swagger / OpenAPI
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API endpoints
    path('api/auth/', include('apps.authentication.urls')),
    path('api/pacientes/', include('apps.etl.urls')),
    path('api/etl/', include('apps.etl.etl_urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/ml/', include('apps.ml.urls')),
    path('api/reportes/', include('apps.reports.urls')),

    # Frontend views
    path('', include('apps.dashboard.frontend_urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
