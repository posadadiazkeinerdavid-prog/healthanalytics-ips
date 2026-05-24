from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, LogoutView, UserProfileView, UserListCreateView, UserDetailView, me_view

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('me/', me_view, name='auth-me'),
    path('profile/', UserProfileView.as_view(), name='auth-profile'),
    path('usuarios/', UserListCreateView.as_view(), name='user-list'),
    path('usuarios/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
