#!/usr/bin/env python
"""
Cleanup script to find and fix PropertySale and Property records with NULL IDs.

This script identifies and handles:
1. PropertySale records with NULL IDs
2. Property records with NULL primary keys
3. Related records that reference these invalid records

Run with: python cleanup_null_ids.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from django.db import connection
from estate.models import PropertySale, Property, Payment, Commission
from decimal import Decimal

def find_null_id_property_sales():
    """Find PropertySale records with NULL IDs using raw SQL"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, reference_number, client_name, created_at
            FROM estate_propertysale
            WHERE id IS NULL
        """)
        return cursor.fetchall()

def find_null_id_properties():
    """Find Property records with NULL IDs using raw SQL"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, location, created_at
            FROM estate_property
            WHERE id IS NULL
        """)
        return cursor.fetchall()

def find_property_sales_with_null_property():
    """Find PropertySale records that reference NULL property_item"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ps.id, ps.reference_number, ps.property_item_id, ps.client_name
            FROM estate_propertysale ps
            LEFT JOIN estate_property p ON ps.property_item_id = p.id
            WHERE ps.property_item_id IS NOT NULL AND p.id IS NULL
        """)
        return cursor.fetchall()

def delete_null_id_records():
    """Delete records with NULL IDs using raw SQL"""
    deleted_sales = 0
    deleted_properties = 0
    
    with connection.cursor() as cursor:
        # Delete PropertySales with NULL IDs
        cursor.execute("""
            DELETE FROM estate_propertysale
            WHERE id IS NULL
        """)
        deleted_sales = cursor.rowcount
        
        # Delete Properties with NULL IDs
        cursor.execute("""
            DELETE FROM estate_property
            WHERE id IS NULL
        """)
        deleted_properties = cursor.rowcount
    
    return deleted_sales, deleted_properties

def fix_orphaned_property_sales():
    """Fix PropertySale records that reference non-existent properties"""
    fixed = 0
    
    # Find PropertySales with invalid property_item references
    orphaned_sales = find_property_sales_with_null_property()
    
    if not orphaned_sales:
        return fixed
    
    # Get a default property to use as fallback
    default_property = Property.objects.first()
    
    if not default_property:
        print("⚠️  WARNING: No default property found. Cannot fix orphaned sales.")
        return fixed
    
    for sale_data in orphaned_sales:
        sale_id = sale_data[0]
        try:
            sale = PropertySale.objects.get(id=sale_id)
            sale.property_item = default_property
            sale.save()
            fixed += 1
            print(f"  ✓ Fixed PropertySale {sale_id} (reference: {sale.reference_number})")
        except PropertySale.DoesNotExist:
            print(f"  ✗ PropertySale {sale_id} not found")
        except Exception as e:
            print(f"  ✗ Error fixing PropertySale {sale_id}: {str(e)}")
    
    return fixed

def main():
    print("=" * 60)
    print("NULL ID Cleanup Script")
    print("=" * 60)
    print()
    
    # Find NULL ID PropertySales
    print("1. Checking for PropertySale records with NULL IDs...")
    null_sales = find_null_id_property_sales()
    if null_sales:
        print(f"   ⚠️  Found {len(null_sales)} PropertySale records with NULL IDs:")
        for sale in null_sales:
            print(f"      - Reference: {sale[1]}, Client: {sale[2]}, Created: {sale[3]}")
    else:
        print("   ✓ No PropertySale records with NULL IDs found")
    print()
    
    # Find NULL ID Properties
    print("2. Checking for Property records with NULL IDs...")
    null_properties = find_null_id_properties()
    if null_properties:
        print(f"   ⚠️  Found {len(null_properties)} Property records with NULL IDs:")
        for prop in null_properties:
            print(f"      - Name: {prop[1]}, Location: {prop[2]}, Created: {prop[3]}")
    else:
        print("   ✓ No Property records with NULL IDs found")
    print()
    
    # Find orphaned PropertySales
    print("3. Checking for PropertySale records with invalid property references...")
    orphaned = find_property_sales_with_null_property()
    if orphaned:
        print(f"   ⚠️  Found {len(orphaned)} PropertySale records with invalid property references:")
        for sale in orphaned:
            print(f"      - ID: {sale[0]}, Reference: {sale[1]}, Property ID: {sale[2]}, Client: {sale[3]}")
    else:
        print("   ✓ No orphaned PropertySale records found")
    print()
    
    # Summary
    total_issues = len(null_sales) + len(null_properties) + len(orphaned)
    
    if total_issues == 0:
        print("✅ No issues found! Database is clean.")
        return
    
    print("=" * 60)
    print(f"SUMMARY: Found {total_issues} issues")
    print("=" * 60)
    print()
    
    # Ask for confirmation
    response = input("Do you want to fix these issues? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Cleanup cancelled. No changes made.")
        return
    
    print()
    print("Starting cleanup...")
    print()
    
    # Fix orphaned PropertySales first
    if orphaned:
        print("Fixing orphaned PropertySale records...")
        fixed = fix_orphaned_property_sales()
        print(f"   ✓ Fixed {fixed} orphaned PropertySale records")
        print()
    
    # Delete NULL ID records
    if null_sales or null_properties:
        print("Deleting records with NULL IDs...")
        deleted_sales, deleted_properties = delete_null_id_records()
        print(f"   ✓ Deleted {deleted_sales} PropertySale records with NULL IDs")
        print(f"   ✓ Deleted {deleted_properties} Property records with NULL IDs")
        print()
    
    print("=" * 60)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart your Django application")
    print("2. Monitor logs for any remaining issues")
    print("3. Consider adding database constraints to prevent future issues")

if __name__ == '__main__':
    main()

