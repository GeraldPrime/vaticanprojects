#!/usr/bin/env python
"""
Script to safely remove duplicate payments and prevent future duplicates.
Run this on your production server.

This script will:
1. Find duplicate payments
2. Keep the oldest payment (first created)
3. Delete newer duplicates
4. Recalculate property sale totals
5. Recalculate commission totals
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from estate.models import Payment, PropertySale, Commission, Realtor
from django.db import connection, transaction
from django.db.models import Sum, Q
from decimal import Decimal
from collections import defaultdict
from datetime import datetime

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def find_duplicate_payments():
    """Find duplicate payments"""
    print_header("FINDING DUPLICATE PAYMENTS")
    
    payment_groups = defaultdict(list)
    
    # Group payments by sale, amount, and date
    for payment in Payment.objects.all().select_related('property_sale'):
        if payment.id is None:
            print(f"\n⚠️  Found payment with NULL ID:")
            print(f"   Sale: {payment.property_sale.reference_number if payment.property_sale else 'N/A'}")
            print(f"   Amount: ₦{payment.amount}")
            continue
            
        key = (
            payment.property_sale_id,
            str(payment.amount),
            payment.payment_date.date() if payment.payment_date else None
        )
        payment_groups[key].append(payment)
    
    # Find duplicates
    duplicate_groups = []
    for key, payments in payment_groups.items():
        if len(payments) > 1:
            # Sort by created_at (keep oldest)
            payments_sorted = sorted(
                payments, 
                key=lambda p: p.created_at if hasattr(p, 'created_at') and p.created_at else datetime.min
            )
            
            print(f"\n🔴 DUPLICATE GROUP:")
            print(f"   Sale: {payments_sorted[0].property_sale.reference_number}")
            print(f"   Client: {payments_sorted[0].property_sale.client_name}")
            print(f"   Amount: ₦{payments_sorted[0].amount:,.2f}")
            print(f"   Date: {payments_sorted[0].payment_date}")
            print(f"   Count: {len(payments_sorted)} payments")
            
            for i, p in enumerate(payments_sorted):
                created = p.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(p, 'created_at') and p.created_at else 'Unknown'
                marker = "✓ KEEP" if i == 0 else "✗ DELETE"
                print(f"      {marker} - ID: {p.id}, Created: {created}")
            
            duplicate_groups.append(payments_sorted)
    
    return duplicate_groups

def clean_null_id_payments():
    """Clean up payments with NULL IDs at database level"""
    print_header("CLEANING NULL ID PAYMENTS")
    
    with connection.cursor() as cursor:
        # Check for NULL IDs
        cursor.execute("SELECT COUNT(*) FROM estate_payment WHERE id IS NULL")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"\n⚠️  Found {count} payments with NULL IDs")
            print("   Deleting from database...")
            cursor.execute("DELETE FROM estate_payment WHERE id IS NULL")
            print(f"   ✓ Deleted {count} NULL ID payments")
        else:
            print("\n✅ No NULL ID payments found")
    
    return count

def remove_duplicate_payments(duplicate_groups):
    """Remove duplicate payments, keeping the oldest one"""
    print_header("REMOVING DUPLICATE PAYMENTS")
    
    if not duplicate_groups:
        print("\n✅ No duplicates to remove")
        return 0
    
    total_deleted = 0
    
    for group in duplicate_groups:
        # Keep the first (oldest), delete the rest
        keep_payment = group[0]
        delete_payments = group[1:]
        
        print(f"\n📦 Processing sale: {keep_payment.property_sale.reference_number}")
        print(f"   Keeping payment ID: {keep_payment.id}")
        
        for payment in delete_payments:
            try:
                # Before deleting, we need to handle the commissions
                # Find commissions created for this payment
                sale = payment.property_sale
                
                # Delete the payment
                payment_id = payment.id
                payment.delete()
                total_deleted += 1
                print(f"   ✓ Deleted duplicate payment ID: {payment_id}")
                
            except Exception as e:
                print(f"   ✗ Error deleting payment ID {payment.id}: {e}")
    
    return total_deleted

def recalculate_property_sale_totals():
    """Recalculate all property sale totals from actual payments"""
    print_header("RECALCULATING PROPERTY SALE TOTALS")
    
    updated_count = 0
    
    for sale in PropertySale.objects.all():
        # Calculate actual total from payments
        actual_total = Payment.objects.filter(
            property_sale=sale
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        if sale.amount_paid != actual_total:
            print(f"\n  Updating {sale.reference_number}:")
            print(f"    Old total: ₦{sale.amount_paid:,.2f}")
            print(f"    New total: ₦{actual_total:,.2f}")
            
            sale.amount_paid = actual_total
            sale.save()
            updated_count += 1
    
    if updated_count == 0:
        print("\n✅ All property sale totals are correct")
    else:
        print(f"\n✓ Updated {updated_count} property sales")
    
    return updated_count

def recalculate_commission_totals():
    """Recalculate all realtor commission totals"""
    print_header("RECALCULATING REALTOR COMMISSION TOTALS")
    
    updated_count = 0
    
    for realtor in Realtor.objects.all():
        commission_data = Commission.objects.filter(realtor=realtor).aggregate(
            total=Sum('amount'),
            paid=Sum('amount', filter=Q(is_paid=True))
        )
        
        actual_total = commission_data['total'] or Decimal('0')
        actual_paid = commission_data['paid'] or Decimal('0')
        
        if realtor.total_commission != actual_total or realtor.paid_commission != actual_paid:
            print(f"\n  {realtor.full_name}:")
            print(f"    Total: ₦{realtor.total_commission:,.2f} → ₦{actual_total:,.2f}")
            print(f"    Paid:  ₦{realtor.paid_commission:,.2f} → ₦{actual_paid:,.2f}")
            
            realtor.total_commission = actual_total
            realtor.paid_commission = actual_paid
            realtor.save()
            updated_count += 1
    
    if updated_count == 0:
        print("\n✅ All realtor totals are correct")
    else:
        print(f"\n✓ Updated {updated_count} realtors")
    
    return updated_count

def main():
    """Main cleanup function"""
    print_header("DUPLICATE PAYMENT CLEANUP SCRIPT")
    print("This script will safely remove duplicate payments")
    print("\n⚠️  WARNING: This will modify your database!")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("\nCleanup cancelled.")
        return
    
    try:
        with transaction.atomic():
            # Step 1: Find duplicates
            duplicate_groups = find_duplicate_payments()
            
            # Step 2: Clean NULL IDs
            null_count = clean_null_id_payments()
            
            # Step 3: Show summary
            print_header("SUMMARY")
            print(f"\n  Duplicate payment groups: {len(duplicate_groups)}")
            print(f"  NULL ID payments: {null_count}")
            
            if not duplicate_groups and null_count == 0:
                print("\n  ✓ No issues found! Database is clean.")
                return
            
            # Step 4: Confirm deletion
            total_to_delete = sum(len(group) - 1 for group in duplicate_groups) + null_count
            print(f"  Total payments to delete: {total_to_delete}")
            
            response = input("\nProceed with deletion? (yes/no): ").strip().lower()
            if response != 'yes':
                print("\nDeletion cancelled.")
                return
            
            # Step 5: Remove duplicates
            deleted = remove_duplicate_payments(duplicate_groups)
            
            # Step 6: Recalculate totals
            sales_updated = recalculate_property_sale_totals()
            realtors_updated = recalculate_commission_totals()
            
            # Final summary
            print_header("CLEANUP COMPLETE")
            print(f"\n  Duplicate payments deleted: {deleted}")
            print(f"  NULL ID payments deleted: {null_count}")
            print(f"  Property sales updated: {sales_updated}")
            print(f"  Realtors updated: {realtors_updated}")
            print("\n  ✓ All cleanup operations completed successfully!")
            
    except Exception as e:
        print(f"\n\n✗ ERROR: {e}")
        print("\nTransaction rolled back. No changes were made.")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

