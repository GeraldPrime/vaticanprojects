from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from decimal import Decimal
from .models import User, Realtor, Commission, Property, PropertySale, Payment, FormUpload,Gallery, General

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'last_login', "image")
    search_fields = ('username', 'email',)
    readonly_fields = ('date_joined', 'last_login')

admin.site.register(User, CustomUserAdmin)

@admin.register(Realtor)
class RealtorAdmin(admin.ModelAdmin):
    list_display = ["id", 'full_name', 'email', 'phone', 'referral_code', 'display_image', 
                    'total_commission', 'paid_commission', 'unpaid_commission', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'referral_code']
    readonly_fields = ['total_commission', 'paid_commission', 'unpaid_commission', 'created_at', 'updated_at']
    fieldsets = [
        ('Personal Information', {
            'fields': [('first_name', 'last_name'), 'email', 'phone', 'image', 'address', 'country']
        }),
        ('Banking Details', {
            'fields': ['account_number', 'bank_name']
        }),
        ('Referral System', {   
            'fields': ['referral_code', 'sponsor_code', 'sponsor']
        }),
        ('Commission Information', {
            'fields': ['total_commission', 'paid_commission', 'unpaid_commission']
        }),
        ('System Information', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Profile'

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['realtor', 'amount', 'description', 'is_paid', 'paid_date', 'created_at']
    list_filter = ['is_paid', 'created_at', 'paid_date']
    search_fields = ['realtor__first_name', 'realtor__last_name', 'property_reference', 'description']
    readonly_fields = ['created_at']
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        for commission in queryset.filter(is_paid=False):
            commission.mark_as_paid()
        self.message_user(request, f"{queryset.filter(is_paid=False).count()} commissions marked as paid.")
    mark_as_paid.short_description = "Mark selected commissions as paid"

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'address', 'created_at')
    list_filter = ('location',)
    search_fields = ('name', 'address')

# @admin.register(PropertySale)
# class PropertySaleAdmin(admin.ModelAdmin):
#     list_display = ('reference_number_display', 'property_display', 'client_name_display', 
#                    'selling_price_display', 'amount_paid_display', 'balance_due_display')
#     # Remove list_filter completely since created_at isn't accessible
#     search_fields = ('client_name', 'property__name')
    
#     fieldsets = [
#         ('Property Information', {
#             'fields': ['property_item','description', 'quantity']
#         }),
#         ('Client Information', {
#             'fields': ['client_name', 'client_address', 'client_phone']
#         }),
#         ('Next of Kin', {
#             'fields': ['next_of_kin_name', 'next_of_kin_address', 'next_of_kin_phone']
#         }),
#         ('Pricing', {
#             'fields': ['original_price', 'selling_price', 'amount_paid']
#         }),
#         ('Realtor & Commission', {
#             'fields': ['realtor', 'realtor_commission_percentage', 'sponsor_commission_percentage', 'upline_commission_percentage']
#         }),
#     ]
    
#     def reference_number_display(self, obj):
#         return obj.reference_number
#     reference_number_display.short_description = 'Reference Number'
    
#     def property_display(self, obj):
#         return obj.property_item.name
#     property_display.short_description = 'Property'
    
#     def client_name_display(self, obj):
#         return obj.client_name
#     client_name_display.short_description = 'Client Name'
    
#     def selling_price_display(self, obj):
#         return f"₦{obj.selling_price.quantize(Decimal('0.01'))}"
#     selling_price_display.short_description = 'Selling Price'
    
#     def amount_paid_display(self, obj):
#         return f"₦{obj.amount_paid.quantize(Decimal('0.01'))}"
#     amount_paid_display.short_description = 'Amount Paid'
    
#     def balance_due_display(self, obj):
#         return f"₦{obj.balance_due.quantize(Decimal('0.01'))}"
#     balance_due_display.short_description = 'Balance Due'


@admin.register(PropertySale)
class PropertySaleAdmin(admin.ModelAdmin):
    list_display = ('reference_number_display', 'property_display', 'client_name_display', 
                   'selling_price_display', 'amount_paid_display', 'balance_due_display')
    # list_filter is removed as created_at isn't accessible
    search_fields = ('client_name', 'property_item__name')
    
    fieldsets = [
        ('Property Information', {
            'fields': ['property_type', 'property_item', 'description', 'quantity']
        }),
        ('Client Information', {
            'fields': [
                'client_name', 'client_address', 'client_phone', 'client_email',
                'marital_status', 'spouse_name', 'spouse_phone'
            ]
        }),
        ('Client Identification', {
            'fields': [
                'id_type', 'id_number',
                'lga_of_origin', 'town_of_origin', 'state_of_origin'
            ]
        }),
        ('Client Bank Details', {
            'fields': [
                'bank_name', 'account_number', 'account_name'
            ]
        }),
        ('Next of Kin', {
            'fields': ['next_of_kin_name', 'next_of_kin_address', 'next_of_kin_phone']
        }),
        ('Pricing & Payment', {
            'fields': [
                'original_price', 'selling_price', 'amount_paid', 'payment_plan'
            ]
        }),
        ('Realtor & Commission', {
            'fields': ['realtor', 'realtor_commission_percentage', 'sponsor_commission_percentage', 'upline_commission_percentage']
        }),
    ]
    
    def reference_number_display(self, obj):
        return obj.reference_number
    reference_number_display.short_description = 'Reference Number'
    
    def property_display(self, obj):
        return obj.property_item.name
    property_display.short_description = 'Property'
    
    def client_name_display(self, obj):
        return obj.client_name
    client_name_display.short_description = 'Client Name'
    
    def selling_price_display(self, obj):
        return f"₦{obj.selling_price.quantize(Decimal('0.01'))}"
    selling_price_display.short_description = 'Selling Price'
    
    def amount_paid_display(self, obj):
        return f"₦{obj.amount_paid.quantize(Decimal('0.01'))}"
    amount_paid_display.short_description = 'Amount Paid'
    
    def balance_due_display(self, obj):
        return f"₦{obj.balance_due.quantize(Decimal('0.01'))}"
    balance_due_display.short_description = 'Balance Due'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('property_sale_display', 'amount_display', 'payment_method_display')
    search_fields = ('property_sale__client_name',)
    
    def property_sale_display(self, obj):
        return obj.property_sale.reference_number
    property_sale_display.short_description = 'Property Sale'
    
    def amount_display(self, obj):
        return f"₦{obj.amount.quantize(Decimal('0.01'))}"
    amount_display.short_description = 'Amount'
    
    def payment_method_display(self, obj):
        return obj.payment_method
    payment_method_display.short_description = 'Payment Method'
    
    
@admin.register(FormUpload)
class FormUploadAdmin(admin.ModelAdmin):
    list_display = ('name', 'file_type', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('file_type',)
    
    fieldsets = (
        ('Form Information', {
            'fields': ('name', 'description', 'form_file')
        }),
        ('Metadata', {
            'fields': ('file_type', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title','description','display_image', 'created_at', 'updated_at')
    
    
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Profile'
    

@admin.register(General)
class GeneralAdmin(admin.ModelAdmin):
    list_display = ('company_bank_name', 'company_account_name', 'company_account_number')
    search_fields = ('company_bank_name', 'company_account_name', 'company_account_number')
    list_filter = ('company_bank_name',)