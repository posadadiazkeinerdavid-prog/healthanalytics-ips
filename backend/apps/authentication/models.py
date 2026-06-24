"""
Authentication Models - Custom User with Role-Based Access
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMINISTRADOR)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ADMINISTRADOR = 'administrador'
    MEDICO = 'medico'
    ANALISTA = 'analista'

    ROLES = [
        (ADMINISTRADOR, 'Administrador'),
        (MEDICO, 'Médico'),
        (ANALISTA, 'Analista'),
    ]

    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    role = models.CharField(max_length=20, choices=ROLES, default=ANALISTA, verbose_name='Rol')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres', 'apellidos']

    class Meta:
        db_table = 'auth_users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombres} {self.apellidos} ({self.role})'

    @property
    def full_name(self):
        return f'{self.nombres} {self.apellidos}'

    def has_role(self, role):
        return self.role == role

    def is_admin(self):
        return self.role == self.ADMINISTRADOR

    def is_medico(self):
        return self.role == self.MEDICO

    def is_analista(self):
        return self.role == self.ANALISTA
