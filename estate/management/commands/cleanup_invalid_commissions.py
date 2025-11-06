"""
Management command to clean up invalid commission records.
This command identifies and removes commission records with NULL IDs or other data integrity issues.
"""

from django.core.management.base import BaseCommand
from django.db import connection, models
from estate.models import Commission, Realtor
from decimal import Decimal


class Command(BaseCommand):
    help = 'Clean up invalid commission records with NULL IDs or data integrity issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--fix-totals',
            action='store_true',
            help='Recalculate realtor commission totals after cleanup',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fix_totals = options['fix_totals']

        self.stdout.write(self.style.WARNING('Starting commission cleanup...'))
        
        # Find commissions with NULL or invalid data
        invalid_commissions = []
        
        # Check for commissions that might have issues
        all_commissions = Commission.objects.all()
        
        for commission in all_commissions:
            # Check if commission has valid ID
            if commission.id is None:
                invalid_commissions.append(commission)
                self.stdout.write(
                    self.style.ERROR(
                        f'Found commission with NULL ID: '
                        f'Realtor: {commission.realtor}, '
                        f'Amount: {commission.amount}, '
                        f'Description: {commission.description}'
                    )
                )
        
        # Also check database directly for orphaned records
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, realtor_id, amount, description, property_reference
                FROM estate_commission
                WHERE id IS NULL OR realtor_id IS NULL
            """)
            db_invalid = cursor.fetchall()
            
            if db_invalid:
                self.stdout.write(
                    self.style.ERROR(
                        f'Found {len(db_invalid)} invalid records in database'
                    )
                )
                for record in db_invalid:
                    self.stdout.write(f'  - Record: {record}')

        if not invalid_commissions and not db_invalid:
            self.stdout.write(self.style.SUCCESS('No invalid commissions found!'))
            return

        # Show summary
        self.stdout.write(
            self.style.WARNING(
                f'\nFound {len(invalid_commissions)} invalid commission objects'
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\n[DRY RUN] No changes will be made. '
                    'Run without --dry-run to actually delete these records.'
                )
            )
            return

        # Delete invalid commissions
        if invalid_commissions:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDeleting {len(invalid_commissions)} invalid commissions...'
                )
            )
            
            for commission in invalid_commissions:
                try:
                    commission.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Deleted invalid commission')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ Error deleting commission: {e}')
                    )

        # Clean up database-level issues
        if db_invalid:
            with connection.cursor() as cursor:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nCleaning up {len(db_invalid)} database-level issues...'
                    )
                )
                cursor.execute("""
                    DELETE FROM estate_commission
                    WHERE id IS NULL OR realtor_id IS NULL
                """)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Cleaned up database records'
                    )
                )

        # Recalculate realtor totals if requested
        if fix_totals:
            self.stdout.write(
                self.style.WARNING('\nRecalculating realtor commission totals...')
            )
            
            for realtor in Realtor.objects.all():
                # Calculate actual total from commissions
                actual_total = Commission.objects.filter(
                    realtor=realtor
                ).aggregate(
                    total=models.Sum('amount')
                )['total'] or Decimal('0')
                
                # Calculate actual paid total
                actual_paid = Commission.objects.filter(
                    realtor=realtor,
                    is_paid=True
                ).aggregate(
                    total=models.Sum('amount')
                )['total'] or Decimal('0')
                
                # Update if different
                if realtor.total_commission != actual_total or realtor.paid_commission != actual_paid:
                    old_total = realtor.total_commission
                    old_paid = realtor.paid_commission
                    
                    realtor.total_commission = actual_total
                    realtor.paid_commission = actual_paid
                    realtor.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Updated {realtor.full_name}: '
                            f'Total: ₦{old_total} → ₦{actual_total}, '
                            f'Paid: ₦{old_paid} → ₦{actual_paid}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Commission cleanup completed successfully!')
        )

