import os
import django
from decimal import Decimal
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vaticanprojects.settings')
django.setup()

from estate.models import Realtor, Property, PropertySale, Payment, User

def reproduce_property_sale_issue():
    print("Testing property sale registration...")
    try:
        # Get or create a realtor
        realtor, _ = Realtor.objects.get_or_create(
            referral_code="TEST1234",
            defaults={'first_name': "Test", 'last_name': "Realtor", 'email': "test@example.com"}
        )
        
        # Get or create a property
        prop, _ = Property.objects.get_or_create(
            name="Test Property",
            defaults={
                'location': "lagos", 
                'description': "Test Description",
                'address': "Test Address"
            }
        )
        
        # Mock request.user
        user, _ = User.objects.get_or_create(username="admin")
        
        print(f"Using Realtor: {realtor.id}, Property: {prop.id}")
        
        from django.db import transaction
        with transaction.atomic():
            # Mimic views.py logic
            property_sale = PropertySale.objects.create(
                description="Test Sale",
                property_type="land",
                property_item=prop,
                quantity=1,
                client_name="Test Client",
                payment_plan=None,
                # Add pricing section
                discount=Decimal('0'),
                realtor=realtor,
                realtor_commission_percentage=Decimal('10'),
                sponsor_commission_percentage=Decimal('5'),
                upline_commission_percentage=Decimal('2'),
            )
            
            print(f"PropertySale created with PK: {property_sale.pk}")
            
            initial_payment = Decimal('1000000')
            if initial_payment > 0:
                property_sale.amount_paid = initial_payment
                property_sale.save()
                print("PropertySale saved with initial payment.")
                
                Payment.objects.create(
                    property_sale=property_sale,
                    amount=initial_payment,
                    payment_method="Cash",
                    notes="Initial payment at registration",
                    payment_date=timezone.now()
                )
                print("Payment record created.")

        print("Success! Property sale registered without errors.")
        
    except Exception as e:
        print(f"FAILED to register property sale. Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce_property_sale_issue()
