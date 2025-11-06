# Fake Realtors Cleanup Instructions

## Problem
Fake realtor registrations with foreign phone numbers (e.g., +1-956-402-5253) have been created through the public registration form.

## Solution Implemented

### 1. **Prevention (Already Deployed)**
Added validation to the `realtor_register` view to:
- ✅ Only accept Nigerian phone numbers (formats: +2348012345678, 08012345678, 2348012345678)
- ✅ Only accept "Nigeria" as the country
- ✅ Reject any foreign phone numbers or countries

This prevents future fake registrations.

### 2. **Cleanup (To Be Run on Server)**

## Steps to Clean Up Fake Realtors

### **Step 1: Push Changes to Server**

On your local machine:
```bash
cd /Users/admin/Desktop/vaticanprojects
git push origin main
```

### **Step 2: SSH into Server**

```bash
ssh root@72.61.167.164
```

### **Step 3: Navigate to Project and Pull Changes**

```bash
cd /opt/vaticanprojects/vaticanprojects/vaticanprojects
source /opt/vaticanprojects/bin/activate
git pull origin main
```

### **Step 4: Run the Cleanup Script**

#### **Option A: Interactive Mode (Recommended)**

```bash
python manage.py shell
```

Then paste this script:

```python
from estate.models import Realtor
from django.db import transaction
import re

print("\n" + "="*70)
print("FINDING SUSPICIOUS/FAKE REALTOR REGISTRATIONS")
print("="*70)

suspicious_realtors = []

# Foreign phone patterns
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
]

print("\nSearching for realtors with foreign phone numbers...")

for realtor in Realtor.objects.all():
    phone = realtor.phone.strip() if realtor.phone else ""
    
    is_foreign = False
    for pattern in foreign_phone_patterns:
        if re.match(pattern, phone):
            is_foreign = True
            break
    
    if is_foreign:
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
    print()

# Separate safe and needs review
safe_to_delete = [d for d in suspicious_realtors if d['sales'] == 0 and d['commissions'] == 0 and d['referrals'] == 0]
needs_review = [d for d in suspicious_realtors if d['sales'] > 0 or d['commissions'] > 0 or d['referrals'] > 0]

print("="*70)
print("SUMMARY")
print("="*70)
print(f"\nSafe to delete (no activity): {len(safe_to_delete)}")
print(f"Needs review (has activity): {len(needs_review)}")

if safe_to_delete:
    print("\n✅ SAFE TO DELETE:")
    for i, data in enumerate(safe_to_delete, 1):
        r = data['realtor']
        print(f"   {i}. {r.full_name} - {r.phone} - {r.email}")

if needs_review:
    print("\n⚠️  NEEDS REVIEW (DO NOT DELETE):")
    for i, data in enumerate(needs_review, 1):
        r = data['realtor']
        print(f"   {i}. {r.full_name} - Sales: {data['sales']}, Commissions: {data['commissions']}, Referrals: {data['referrals']}")

# Don't delete yet - wait for confirmation
print("\n" + "="*70)
print("Review the list above before proceeding with deletion")
print("="*70)
```

**Review the output carefully!** Make sure the realtors listed as "Safe to delete" are indeed fake.

#### **Step 5: Delete the Fake Realtors**

After reviewing, if you're sure, run this in the same shell:

```python
# Delete safe ones
if safe_to_delete:
    print(f"\nDeleting {len(safe_to_delete)} fake realtors...")
    
    with transaction.atomic():
        deleted_count = 0
        for data in safe_to_delete:
            realtor = data['realtor']
            print(f"Deleting: {realtor.full_name} - {realtor.phone}")
            realtor.delete()
            deleted_count += 1
        
        print(f"\n✅ Successfully deleted {deleted_count} fake realtors")
else:
    print("\n✅ No fake realtors to delete")

exit()
```

### **Step 6: Restart the Service**

```bash
systemctl restart vaticanprojects.service
systemctl status vaticanprojects.service
```

### **Step 7: Test**

Visit the admin portal and verify:
- The fake realtors are gone
- Try registering with a foreign phone number - should be rejected
- Try registering with a Nigerian phone number - should work

## What Changed

### **Files Modified:**

1. **`estate/views.py`** (lines 2840-2861)
   - Added Nigerian phone number validation using regex pattern: `^(\+?234|0)[7-9][0-1]\d{8}$`
   - Added country validation (must be "Nigeria")
   - Rejects foreign phone numbers with clear error messages

2. **`estate/templates/user/realtors_page.html`** (line 175)
   - Fixed `ValueError` when displaying realtor commission totals

3. **`cleanup_fake_realtors.py`** (new file)
   - Standalone script to identify and remove fake realtors
   - Can be run via Django shell

## Nigerian Phone Number Format

The validation accepts these formats:
- `+2348012345678` (international format)
- `2348012345678` (without + sign)
- `08012345678` (local format)

Valid prefixes: 070x, 080x, 081x, 090x, 091x (where x is 0-9)

## Prevention Going Forward

✅ **Validation is now active** - Any new registration attempts with:
- Foreign phone numbers → Rejected
- Non-Nigerian country → Rejected
- Invalid Nigerian phone format → Rejected

## Notes

- **DO NOT delete realtors with sales, commissions, or referrals** - they may be legitimate
- The script identifies them as "Needs Review"
- For those, manually verify if they're real or fake before taking action
- Always backup the database before bulk deletions

## Support

If you encounter any issues:
1. Check the Django logs: `tail -f /opt/vaticanprojects/vaticanprojects/vaticanprojects/django.log`
2. Check the service status: `systemctl status vaticanprojects.service`
3. Review the error messages carefully

