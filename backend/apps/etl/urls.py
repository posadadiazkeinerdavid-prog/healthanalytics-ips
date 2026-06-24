from django.urls import path
from .views import PacienteListView, PacienteDetailView

urlpatterns = [
    path('', PacienteListView.as_view(), name='paciente-list'),
    path('<int:pk>/', PacienteDetailView.as_view(), name='paciente-detail'),
]
