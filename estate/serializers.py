# serializers.py
from rest_framework import serializers
from .models import Property, PropertySale, Payment, Realtor, CommissionSetting

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class RealtorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Realtor
        fields = ['id', 'sponsor_code', 'sponsor', 'full_name']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_date', 'reference']

class PropertySaleSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    realtor_details = RealtorSerializer(source='realtor', read_only=True)
    property_details = PropertySerializer(source='property', read_only=True)
    commissions = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertySale
        fields = '__all__'
        read_only_fields = ['reference_number']
    
    def get_commissions(self, obj):
        # Get commission settings
        commission_settings = CommissionSetting.objects.filter(property_type=obj.property_type)
        percentages = [0, 0, 0]  # Default percentages
        
        for setting in commission_settings:
            percentages[setting.level] = float(setting.percentage)
        
        return obj.calculate_commission(percentages)
    
    def get_total_paid(self, obj):
        return sum(payment.amount for payment in obj.payments.all())
    
    def get_remaining_amount(self, obj):
        total_paid = self.get_total_paid(obj)
        return float(obj.selling_price) - total_paid

class CommissionSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionSetting
        fields = '__all__'