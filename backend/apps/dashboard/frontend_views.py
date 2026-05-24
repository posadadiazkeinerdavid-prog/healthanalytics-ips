"""
Frontend Views - Serve HTML templates
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def login_page(request):
    return render(request, 'auth/login.html')


def dashboard_page(request):
    return render(request, 'dashboard/index.html')


def etl_page(request):
    return render(request, 'etl/index.html')


def analytics_page(request):
    return render(request, 'analytics/index.html')


def ml_page(request):
    return render(request, 'ml/index.html')


def reports_page(request):
    return render(request, 'reports/index.html')


def pacientes_page(request):
    return render(request, 'dashboard/pacientes.html')
