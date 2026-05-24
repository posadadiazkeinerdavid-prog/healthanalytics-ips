from django.urls import path
from .views import train_view, predict_view, predict_batch_view, model_info_view, model_history_view, predicciones_history_view

urlpatterns = [
    path('train/', train_view, name='ml-train'),
    path('predict/', predict_view, name='ml-predict'),
    path('predict/batch/', predict_batch_view, name='ml-predict-batch'),
    path('info/', model_info_view, name='ml-info'),
    path('historial/', model_history_view, name='ml-history'),
    path('predicciones/', predicciones_history_view, name='ml-predicciones'),
]
