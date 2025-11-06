#!/usr/bin/env python
"""
Script to identify and remove fake realtor registrations
Run this on the server in Django shell: python manage.py shell < cleanup_fake_realtors.py
"""

import os
import django
import re
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from estate.models import Realtor, PropertySale, Commission
from django.db import transaction

print("\n" + "="*70)
print("FINDING SUSPICIOUS/FAKE REALTOR REGISTRATIONS")
print("="*70)

# Criteria for suspicious realtors:
# 1. Foreign phone numbers (not starting with +234, 0, or Nigerian format)
# 2. No sales or commissions
# 3. Recently created (optional)

suspicious_realtors = []

# Find realtors with foreign phone numbers
foreign_phone_patterns = [
    r'^\+1',      # USA/Canada
    r'^\+44',     # UK
    r'^\+91',     # India
    r'^\+86',     # China
    r'^\+81',     # Japan
    r'^\+49',     # Germany
    r'^\+33',     # France
    r'^\+39',     # Italy
    r'^\+61',     # Australia
    r'^\+971',    # UAE
    r'^\+27',     # South Africa
    r'^\+254',    # Kenya
    r'^\+233',    # Ghana
    r'^\+256',    # Uganda
]

print("\nSearching for realtors with foreign phone numbers...")

for realtor in Realtor.objects.all():
    phone = realtor.phone.strip() if realtor.phone else ""
    
    # Check if phone matches any foreign pattern
    is_foreign = False
    for pattern in foreign_phone_patterns:
        if re.match(pattern, phone):
            is_foreign = True
            break
    
    if is_foreign:
        # Check if they have any sales or commissions
        sales_count = realtor.sales.count()
        commissions_count = realtor.commissions.count()
        referrals_count = Realtor.objects.filter(sponsor=realtor).count()
        
        suspicious_realtors.append({
            'realtor': realtor,
            'sales': sales_count,
            'commissions': commissions_count,
            'referrals': referrals_count,
            'total_commission': realtor.total_commission or 0
        })

print(f"\nFound {len(suspicious_realtors)} realtors with foreign phone numbers:\n")

# Display them
for i, data in enumerate(suspicious_realtors, 1):
    r = data['realtor']
    print(f"{i}. {r.full_name} (ID: {r.id})")
    print(f"   Email: {r.email}")
    print(f"   Phone: {r.phone}")
    print(f"   Country: {r.country}")
    print(f"   Referral Code: {r.referral_code}")
    print(f"   Created: {r.created_at}")
    print(f"   Sales: {data['sales']}, Commissions: {data['commissions']}, Referrals: {data['referrals']}")
    print(f"   Total Commission: ₦{data['total_commission']:,.2f}")
    print(f"   Executive: {r.is_executive}")
    print()

# Separate into safe-to-delete and needs-review
safe_to_delete = [d for d in suspicious_realtors if d['sales'] == 0 and d['commissions'] == 0 and d['referrals'] == 0]
needs_review = [d for d in suspicious_realtors if d['sales'] > 0 or d['commissions'] > 0 or d['referrals'] > 0]

print("="*70)
print("SUMMARY")
print("="*70)
print(f"\nSafe to delete (no activity): {len(safe_to_delete)}")
print(f"Needs review (has activity): {len(needs_review)}")

if safe_to_delete:
    print("\n✅ SAFE TO DELETE (No sales, commissions, or referrals):")
    for i, data in enumerate(safe_to_delete, 1):
        r = data['realtor']
        print(f"   {i}. {r.full_name} - {r.phone} - {r.email}")

if needs_review:
    print("\n⚠️  NEEDS REVIEW (Has activity - DO NOT DELETE):")
    for i, data in enumerate(needs_review, 1):
        r = data['realtor']
        print(f"   {i}. {r.full_name} - Sales: {data['sales']}, Commissions: {data['commissions']}, Referrals: {data['referrals']}")

print("\n" + "="*70)
print("DELETION")
print("="*70)

if safe_to_delete:
    print(f"\nPreparing to delete {len(safe_to_delete)} fake realtors...")
    
    response = input("\nType 'DELETE' (in capitals) to confirm deletion: ").strip()
    
    if response == 'DELETE':
        with transaction.atomic():
            deleted_count = 0
            for data in safe_to_delete:
                realtor = data['realtor']
                print(f"Deleting: {realtor.full_name} - {realtor.phone}")
                realtor.delete()
                deleted_count += 1
            
            print(f"\n✅ Successfully deleted {deleted_count} fake realtors")
    else:
        print("\n❌ Deletion cancelled - no changes made")
else:
    print("\n✅ No fake realtors to delete")

print("\n" + "="*70)
print("CLEANUP COMPLETE")
print("="*70)

