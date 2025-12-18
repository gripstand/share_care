from django.core.management.base import BaseCommand
from equipment.models import Equipment, EquipmentStatus
from client.models import Equipment_with_client

class Command(BaseCommand):
    help = 'Syncs the Equipment_with_client table with the latest status history'

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing tracking records...")
        Equipment_with_client.objects.all().delete()

        active_equipment = Equipment.objects.filter(eq_active_status=True)
        migrated_count = 0

        self.stdout.write(f"Checking {active_equipment.count()} active items...")

        for eq in active_equipment:
            # Use the ordering logic we perfected
            latest_status = EquipmentStatus.objects.filter(
                equipment=eq
            ).order_by('-status_date', '-id').first()

            if latest_status and latest_status.status == 'CLIENT':
                Equipment_with_client.objects.create(
                    equipment=eq,
                    client=latest_status.client,
                    date_issued=latest_status.status_date
                )
                migrated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"✅ Success! {migrated_count} records migrated."))