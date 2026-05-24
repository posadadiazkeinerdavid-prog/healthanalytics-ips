"""
Authentication Views - Login, Register, User Management
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, UserProfileSerializer
from .permissions import IsAdministrador


class LoginView(TokenObtainPairView):
    """Endpoint de inicio de sesión con JWT"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class LogoutView(generics.GenericAPIView):
    """Cierre de sesión - invalida el refresh token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Sesión cerrada exitosamente'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Perfil del usuario autenticado"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListCreateView(generics.ListCreateAPIView):
    """Lista y creación de usuarios (solo Administrador)"""
    serializer_class = UserSerializer
    permission_classes = [IsAdministrador]
    queryset = User.objects.all().order_by('-date_joined')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, edición y eliminación de usuario (solo Administrador)"""
    serializer_class = UserSerializer
    permission_classes = [IsAdministrador]
    queryset = User.objects.all()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Retorna la información del usuario autenticado"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)
