#!/usr/bin/env python
"""
Script to clean up invalid commission records on production server.
Run this on your Hostinger VPS with: python cleanup_commissions.py

This script will:
1. Find and delete duplicate/invalid commission records
2. Recalculate realtor commission totals
3. Fix any data integrity issues
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from estate.models import Commission, Realtor, PropertySale, Payment
from django.db import connection, transaction
from django.db.models import Sum, Q
from decimal import Decimal
from collections import defaultdict

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def find_duplicate_commissions():
    """Find duplicate commission records"""
    print_header("FINDING DUPLICATE COMMISSIONS")
    
    # Group commissions by realtor and property_reference
    commission_groups = defaultdict(list)
    
    for commission in Commission.objects.all().select_related('realtor'):
        key = (
            commission.realtor_id,
            commission.property_reference,
            str(commission.amount),
            commission.description
        )
        commission_groups[key].append(commission)
    
    duplicates = []
    for key, commissions in commission_groups.items():
        if len(commissions) > 1:
            # Keep the first one, mark others as duplicates
            duplicates.extend(commissions[1:])
            print(f"\n  Found {len(commissions)} duplicate commissions:")
            print(f"    Realtor: {commissions[0].realtor.full_name}")
            print(f"    Property: {commissions[0].property_reference}")
            print(f"    Amount: ₦{commissions[0].amount}")
            print(f"    IDs: {[c.id for c in commissions]}")
    
    return duplicates

def find_invalid_commissions():
    """Find commissions with NULL or invalid data"""
    print_header("FINDING INVALID COMMISSIONS")
    
    invalid = []
    
    # Check for commissions with NULL realtor
    null_realtor = Commission.objects.filter(realtor__isnull=True)
    if null_realtor.exists():
        print(f"\n  Found {null_realtor.count()} commissions with NULL realtor")
        invalid.extend(list(null_realtor))
    
    # Check for commissions with 0 or negative amounts
    invalid_amount = Commission.objects.filter(Q(amount__lte=0))
    if invalid_amount.exists():
        print(f"  Found {invalid_amount.count()} commissions with invalid amounts")
        invalid.extend(list(invalid_amount))
    
    # Check database directly for NULL IDs
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM estate_commission 
            WHERE id IS NULL OR realtor_id IS NULL
        """)
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"  Found {count} database-level invalid records")
    
    return invalid

def delete_commissions(commissions, label=""):
    """Delete a list of commissions"""
    if not commissions:
        print(f"\n  No {label} to delete")
        return 0
    
    print(f"\n  Deleting {len(commissions)} {label}...")
    
    deleted_count = 0
    for commission in commissions:
        try:
            # Subtract from realtor's total before deleting
            if commission.realtor:
                commission.realtor.total_commission -= commission.amount
                if commission.is_paid:
                    commission.realtor.paid_commission -= commission.amount
                commission.realtor.save()
            
            commission.delete()
            deleted_count += 1
            print(f"    ✓ Deleted commission ID: {commission.id}")
        except Exception as e:
            print(f"    ✗ Error deleting commission ID {commission.id}: {e}")
    
    return deleted_count

def recalculate_realtor_totals():
    """Recalculate all realtor commission totals from scratch"""
    print_header("RECALCULATING REALTOR TOTALS")
    
    updated_count = 0
    
    for realtor in Realtor.objects.all():
        # Calculate actual totals from commissions
        commission_data = Commission.objects.filter(realtor=realtor).aggregate(
            total=Sum('amount'),
            paid=Sum('amount', filter=Q(is_paid=True))
        )
        
        actual_total = commission_data['total'] or Decimal('0')
        actual_paid = commission_data['paid'] or Decimal('0')
        
        # Check if update needed
        if (realtor.total_commission != actual_total or 
            realtor.paid_commission != actual_paid):
            
            print(f"\n  Updating {realtor.full_name}:")
            print(f"    Total: ₦{realtor.total_commission} → ₦{actual_total}")
            print(f"    Paid:  ₦{realtor.paid_commission} → ₦{actual_paid}")
            
            realtor.total_commission = actual_total
            realtor.paid_commission = actual_paid
            realtor.save()
            updated_count += 1
    
    print(f"\n  Updated {updated_count} realtors")
    return updated_count

def clean_database_level_issues():
    """Clean up database-level issues"""
    print_header("CLEANING DATABASE-LEVEL ISSUES")
    
    with connection.cursor() as cursor:
        # Delete records with NULL IDs or NULL realtor_id
        cursor.execute("""
            DELETE FROM estate_commission 
            WHERE id IS NULL OR realtor_id IS NULL
        """)
        deleted = cursor.rowcount
        
        if deleted > 0:
            print(f"\n  Cleaned up {deleted} database-level invalid records")
        else:
            print("\n  No database-level issues found")
        
        return deleted

def main():
    """Main cleanup function"""
    print_header("VATICAN PROJECTS - COMMISSION CLEANUP SCRIPT")
    print("This script will clean up duplicate and invalid commission records")
    print("\nWARNING: This will modify your database!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("\nCleanup cancelled.")
        return
    
    try:
        with transaction.atomic():
            # Step 1: Find duplicates
            duplicates = find_duplicate_commissions()
            
            # Step 2: Find invalid commissions
            invalid = find_invalid_commissions()
            
            # Step 3: Show summary
            print_header("SUMMARY")
            print(f"\n  Duplicate commissions found: {len(duplicates)}")
            print(f"  Invalid commissions found: {len(invalid)}")
            print(f"  Total to delete: {len(duplicates) + len(invalid)}")
            
            if not duplicates and not invalid:
                print("\n  ✓ No issues found! Database is clean.")
                return
            
            # Step 4: Confirm deletion
            response = input("\nProceed with deletion? (yes/no): ").strip().lower()
            if response != 'yes':
                print("\nDeletion cancelled.")
                return
            
            # Step 5: Delete duplicates
            deleted_dup = delete_commissions(duplicates, "duplicate commissions")
            
            # Step 6: Delete invalid
            deleted_inv = delete_commissions(invalid, "invalid commissions")
            
            # Step 7: Clean database-level issues
            deleted_db = clean_database_level_issues()
            
            # Step 8: Recalculate totals
            updated = recalculate_realtor_totals()
            
            # Final summary
            print_header("CLEANUP COMPLETE")
            print(f"\n  Duplicate commissions deleted: {deleted_dup}")
            print(f"  Invalid commissions deleted: {deleted_inv}")
            print(f"  Database-level records cleaned: {deleted_db}")
            print(f"  Realtor totals updated: {updated}")
            print("\n  ✓ All cleanup operations completed successfully!")
            
    except Exception as e:
        print(f"\n\n✗ ERROR: {e}")
        print("\nTransaction rolled back. No changes were made.")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

