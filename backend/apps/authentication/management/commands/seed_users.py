"""
Management command: seed_users
Crea usuarios iniciales del sistema para pruebas
"""

from django.core.management.base import BaseCommand
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Crea usuarios de prueba para el sistema HealthAnalytics IPS'

    def handle(self, *args, **options):
        users = [
            {
                'email': 'admin@healthanalytics.com',
                'password': 'Admin1234!',
                'nombres': 'Carlos',
                'apellidos': 'Administrador',
                'role': User.ADMINISTRADOR,
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'email': 'medico@healthanalytics.com',
                'password': 'Medico1234!',
                'nombres': 'María',
                'apellidos': 'González',
                'role': User.MEDICO,
            },
            {
                'email': 'analista@healthanalytics.com',
                'password': 'Analista1234!',
                'nombres': 'Juan',
                'apellidos': 'Pérez',
                'role': User.ANALISTA,
            },
        ]

        for u in users:
            password = u.pop('password')
            if not User.objects.filter(email=u['email']).exists():
                user = User.objects.create_user(password=password, **u)
                self.stdout.write(self.style.SUCCESS(
                    f"✓ Usuario creado: {user.email} ({user.role})"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"⚠ Ya existe: {u['email']}"
                ))

        self.stdout.write(self.style.SUCCESS('\n¡Usuarios de prueba creados exitosamente!'))
        self.stdout.write('  admin@healthanalytics.com  / Admin1234!')
        self.stdout.write('  medico@healthanalytics.com / Medico1234!')
        self.stdout.write('  analista@healthanalytics.com / Analista1234!')
