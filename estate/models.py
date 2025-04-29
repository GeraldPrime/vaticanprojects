
from django.db import models
import random
import string
from django.utils import timezone
import uuid
from decimal import Decimal
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    date_joined = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='users/', null=True, blank=True)
        
    def __str__(self):
        return self.username

    class Meta:
        app_label = 'estate'


class Realtor(models.Model):
    # Profile Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='realtors/', blank=True, null=True)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    
    # Banking Details
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    
    # Referral System
    referral_code = models.CharField(max_length=8, unique=True)
    sponsor_code = models.CharField(max_length=8, blank=True, null=True)
    sponsor = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='referrals')
    
    # Commission Tracking
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def unpaid_commission(self):
        """Calculate unpaid commission amount"""
        return self.total_commission - self.paid_commission
    
    @property
    def full_name(self):
        """Return the realtor's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Generate unique referral code for new realtors
        if not self.referral_code:
            self.referral_code = self._generate_unique_code()
        
        # Link to sponsor if sponsor_code is provided
        if self.sponsor_code and not self.sponsor:
            try:
                self.sponsor = Realtor.objects.get(referral_code=self.sponsor_code)
            except Realtor.DoesNotExist:
                pass  # Handle invalid sponsor code (could log this)
                
        super().save(*args, **kwargs)
    
    def _generate_unique_code(self):
        """Generate a unique 8-digit numeric referral code"""
        while True:
            # Generate 8-digit numeric code
            code = ''.join(random.choices(string.digits, k=8))
            # Check if code already exists
            if not Realtor.objects.filter(referral_code=code).exists():
                return code
    
    def __str__(self):
        return self.full_name


class Commission(models.Model):
    """Model to track individual commission transactions"""
    realtor = models.ForeignKey(Realtor, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)  # e.g., "Commission for Property XYZ sale"
    property_reference = models.CharField(max_length=100, blank=True, null=True)  # Reference to property sold
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def mark_as_paid(self):
        """Mark this commission as paid and update the realtor's paid_commission"""
        if not self.is_paid:
            self.is_paid = True
            self.paid_date = timezone.now()
            self.save()
            
            # Update realtor's paid commission
            self.realtor.paid_commission += self.amount
            self.realtor.save()
    
    def __str__(self):
        status = "Paid" if self.is_paid else "Unpaid"
        return f"{self.realtor.full_name} - ${self.amount} ({status})"


class Property(models.Model):
    STATES_CHOICES = [
        ('abia', 'Abia'),
        ('adamawa', 'Adamawa'),
        ('akwa_ibom', 'Akwa Ibom'),
        ('anambra', 'Anambra'),
        ('bauchi', 'Bauchi'),
        ('bayelsa', 'Bayelsa'),
        ('benue', 'Benue'),
        ('borno', 'Borno'),
        ('cross_river', 'Cross River'),
        ('delta', 'Delta'),
        ('ebonyi', 'Ebonyi'),
        ('edo', 'Edo'),
        ('ekiti', 'Ekiti'),
        ('enugu', 'Enugu'),
        ('fct', 'Federal Capital Territory'),
        ('gombe', 'Gombe'),
        ('imo', 'Imo'),
        ('jigawa', 'Jigawa'),
        ('kaduna', 'Kaduna'),
        ('kano', 'Kano'),
        ('katsina', 'Katsina'),
        ('kebbi', 'Kebbi'),
        ('kogi', 'Kogi'),
        ('kwara', 'Kwara'),
        ('lagos', 'Lagos'),
        ('nasarawa', 'Nasarawa'),
        ('niger', 'Niger'),
        ('ogun', 'Ogun'),
        ('ondo', 'Ondo'),
        ('osun', 'Osun'),
        ('oyo', 'Oyo'),
        ('plateau', 'Plateau'),
        ('rivers', 'Rivers'),
        ('sokoto', 'Sokoto'),
        ('taraba', 'Taraba'),
        ('yobe', 'Yobe'),
        ('zamfara', 'Zamfara'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=100, choices=STATES_CHOICES)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Properties"


class PropertySale(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('building', 'Building Property'),
        ('land', 'Land'),
    ]
    
    PAYMENT_PLAN_CHOICES = [
        ('outright', 'Outright Purchase'),
        ('3_months', '3 Months Plan'),
        ('6_months', '6 Months Plan'),
    ]
    
    # Generate a unique reference number
    def generate_reference_number():
        return ''.join(uuid.uuid4().hex[:12].upper())
    
    reference_number = models.CharField(max_length=12, default=generate_reference_number, unique=True, editable=False)
    description = models.TextField(max_length=255)
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPE_CHOICES)
    property_item = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='sales')  # Renamed from 'property'
    quantity = models.PositiveIntegerField(help_text="Number of plots or buildings")
    
    # Client information
    client_name = models.CharField(max_length=255)
    client_address = models.TextField()
    client_phone = models.CharField(max_length=20)
    
    # Next of kin information
    next_of_kin_name = models.CharField(max_length=255)
    next_of_kin_address = models.TextField()
    next_of_kin_phone = models.CharField(max_length=20)
    
    # Pricing information
    original_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment plan
    payment_plan = models.CharField(max_length=10, choices=PAYMENT_PLAN_CHOICES, default='outright')
    
    # Realtor and commission tracking
    realtor = models.ForeignKey(Realtor, on_delete=models.CASCADE, related_name='sales')
    realtor_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sponsor_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    upline_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.reference_number} - {self.client_name}"
    
    @property
    def balance_due(self):
        """Calculate the remaining balance to be paid"""
        return self.selling_price - self.amount_paid
    
    @property
    def is_fully_paid(self):
        """Check if the property is fully paid for"""
        return self.balance_due <= Decimal('0')
    
    def calculate_commission(self):
        """Calculate and distribute commission based on the amount paid"""
        if self.amount_paid <= Decimal('0'):
            return
        
        # Get the previously paid amount before this update
        try:
            previous_paid = PropertySale.objects.get(pk=self.pk).amount_paid if self.pk else Decimal('0')
        except PropertySale.DoesNotExist:
            previous_paid = Decimal('0')
        
        # Only calculate commission on the new payment amount
        new_payment_amount = self.amount_paid - previous_paid
        
        if new_payment_amount <= Decimal('0'):
            return
        
        # Calculate commission amounts based on the new payment amount only
        realtor_commission = (new_payment_amount * self.realtor_commission_percentage) / Decimal('100')
        
        # Create commission for the selling realtor
        Commission.objects.create(
            realtor=self.realtor,
            amount=realtor_commission,
            description=f"Commission for property sale {self.reference_number}",
            property_reference=self.reference_number
        )
        
        # Add to realtor's total commission
        self.realtor.total_commission += realtor_commission
        self.realtor.save(update_fields=['total_commission'])
        
        # Process sponsor commission if exists
        if self.realtor.sponsor and self.sponsor_commission_percentage > Decimal('0'):
            sponsor_commission = (new_payment_amount * self.sponsor_commission_percentage) / Decimal('100')
            
            Commission.objects.create(
                realtor=self.realtor.sponsor,
                amount=sponsor_commission,
                description=f"Sponsor commission for property sale {self.reference_number}",
                property_reference=self.reference_number
            )
            
            self.realtor.sponsor.total_commission += sponsor_commission
            self.realtor.sponsor.save(update_fields=['total_commission'])
            
            # Process upline commission if exists
            if self.realtor.sponsor.sponsor and self.upline_commission_percentage > Decimal('0'):
                upline_commission = (new_payment_amount * self.upline_commission_percentage) / Decimal('100')
                
                Commission.objects.create(
                    realtor=self.realtor.sponsor.sponsor,
                    amount=upline_commission,
                    description=f"Upline commission for property sale {self.reference_number}",
                    property_reference=self.reference_number
                )
                
                self.realtor.sponsor.sponsor.total_commission += upline_commission
                self.realtor.sponsor.sponsor.save(update_fields=['total_commission'])
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_amount_paid = Decimal('0')
        
        if not is_new:
            try:
                old_instance = PropertySale.objects.get(pk=self.pk)
                old_amount_paid = old_instance.amount_paid
            except PropertySale.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Check if amount_paid has changed
        if is_new or old_amount_paid != self.amount_paid:
            self.calculate_commission()


class Payment(models.Model):
    property_sale = models.ForeignKey(PropertySale, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, default='Cash')
    reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Only update the property sale's amount_paid if this is a new payment
        if is_new:
            # Recalculate the total from the database to ensure accuracy
            total_payments = Payment.objects.filter(property_sale=self.property_sale).aggregate(
                models.Sum('amount'))['amount__sum'] or Decimal('0')
            
            # Store the old amount_paid before updating
            old_amount_paid = self.property_sale.amount_paid
            
            # Update the property sale with the accurate total
            self.property_sale.amount_paid = total_payments
            
            # Save without triggering the calculate_commission in PropertySale.save()
            PropertySale.objects.filter(pk=self.property_sale.pk).update(amount_paid=total_payments)
            
            # Calculate commissions directly based on the new payment amount only
            new_payment_amount = self.amount
            
            # Calculate commission amounts based on the new payment amount only
            realtor_commission = (new_payment_amount * self.property_sale.realtor_commission_percentage) / Decimal('100')
            
            # Create commission for the selling realtor
            Commission.objects.create(
                realtor=self.property_sale.realtor,
                amount=realtor_commission,
                description=f"Commission for payment on sale {self.property_sale.reference_number}",
                property_reference=self.property_sale.reference_number
            )
            
            # Add to realtor's total commission
            self.property_sale.realtor.total_commission += realtor_commission
            self.property_sale.realtor.save(update_fields=['total_commission'])
            
            # Process sponsor commission if exists
            if self.property_sale.realtor.sponsor and self.property_sale.sponsor_commission_percentage > Decimal('0'):
                sponsor_commission = (new_payment_amount * self.property_sale.sponsor_commission_percentage) / Decimal('100')
                
                Commission.objects.create(
                    realtor=self.property_sale.realtor.sponsor,
                    amount=sponsor_commission,
                    description=f"Sponsor commission for payment on sale {self.property_sale.reference_number}",
                    property_reference=self.property_sale.reference_number
                )
                
                self.property_sale.realtor.sponsor.total_commission += sponsor_commission
                self.property_sale.realtor.sponsor.save(update_fields=['total_commission'])
                
                # Process upline commission if exists
                if self.property_sale.realtor.sponsor.sponsor and self.property_sale.upline_commission_percentage > Decimal('0'):
                    upline_commission = (new_payment_amount * self.property_sale.upline_commission_percentage) / Decimal('100')
                    
                    Commission.objects.create(
                        realtor=self.property_sale.realtor.sponsor.sponsor,
                        amount=upline_commission,
                        description=f"Upline commission for payment on sale {self.property_sale.reference_number}",
                        property_reference=self.property_sale.reference_number
                    )
                    
                    self.property_sale.realtor.sponsor.sponsor.total_commission += upline_commission
                    self.property_sale.realtor.sponsor.sponsor.save(update_fields=['total_commission'])
    
    
    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None
    #     super().save(*args, **kwargs)
        
    #     # Only update the property sale's amount_paid if this is a new payment
    #     if is_new:
    #         # Recalculate the total from the database to ensure accuracy
    #         total_payments = Payment.objects.filter(property_sale=self.property_sale).aggregate(
    #             models.Sum('amount'))['amount__sum'] or Decimal('0')
            
    #         # Update the property sale with the accurate total
    #         self.property_sale.amount_paid = total_payments
    #         self.property_sale.save(update_fields=['amount_paid'])  # Only update this field