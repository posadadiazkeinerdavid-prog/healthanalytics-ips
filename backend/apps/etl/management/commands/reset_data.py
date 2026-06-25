from django.core.management.base import BaseCommand
from apps.etl.models import Paciente, ETLHistory


class Command(BaseCommand):
    help = 'Elimina todos los pacientes y el historial ETL'

    def handle(self, *args, **options):
        count_pacientes = Paciente.objects.count()
        count_historial = ETLHistory.objects.count()
        Paciente.objects.all().delete()
        ETLHistory.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Dashboard limpio: {count_pacientes} pacientes y {count_historial} historiales eliminados'))