"""
Frontend Views - Serve HTML templates
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def login_page(request):
    return render(request, 'auth/login.html')


@login_required
def dashboard_page(request):
    return render(request, 'dashboard/index.html')


@login_required
def etl_page(request):
    return render(request, 'etl/index.html')


@login_required
def analytics_page(request):
    return render(request, 'analytics/index.html')


@login_required
def ml_page(request):
    return render(request, 'ml/index.html')


@login_required
def reports_page(request):
    return render(request, 'reports/index.html')


@login_required
def pacientes_page(request):
    return render(request, 'dashboard/pacientes.html')