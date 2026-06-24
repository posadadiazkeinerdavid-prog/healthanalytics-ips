from django.urls import path
from .views import run_etl_base_dataset, upload_and_run_etl, etl_history_list, etl_history_detail

urlpatterns = [
    path('run/', run_etl_base_dataset, name='etl-run'),
    path('upload/', upload_and_run_etl, name='etl-upload'),
    path('historial/', etl_history_list, name='etl-history'),
    path('historial/<int:pk>/', etl_history_detail, name='etl-history-detail'),
]
