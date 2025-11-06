#!/usr/bin/env python
"""
Script to add a unique constraint to prevent duplicate payments.
This adds a database-level constraint to prevent the same payment from being recorded twice.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from django.core.management import call_command

print("="*70)
print("  ADDING UNIQUE CONSTRAINT TO PREVENT DUPLICATE PAYMENTS")
print("="*70)

print("\nThis will create a migration to add a unique constraint on:")
print("  - property_sale")
print("  - amount")
print("  - payment_date")
print("\nThis prevents the exact same payment from being recorded twice.")

response = input("\nProceed? (yes/no): ").strip().lower()
if response != 'yes':
    print("\nCancelled.")
    sys.exit(0)

# Create the migration
print("\nCreating migration...")
call_command('makemigrations', 'estate', '--empty', '--name', 'add_payment_unique_constraint')

print("\n✓ Migration created!")
print("\nNext steps:")
print("1. Edit the migration file to add the constraint")
print("2. Run: python manage.py migrate")
print("\nOr use the model-based approach (recommended)")

