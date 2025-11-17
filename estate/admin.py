# from pyexpat.errors import messages
from django.contrib import messages
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from decimal import Decimal
from .models import User, Realtor, Commission, Property, PropertySale, Payment, FormUpload,Gallery, General

from django.core.exceptions import ValidationError


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
            'fields': ['account_number', 'bank_name','account_name']
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
#     # list_filter is removed as created_at isn't accessible
#     search_fields = ('client_name', 'property_item__name')
    
#     fieldsets = [
#         ('Property Information', {
#             'fields': ['property_type', 'property_item', 'description', 'quantity']
#         }),
#         ('Client Information', {
#             'fields': [
#                 'client_name', 'client_address', 'client_phone', 'client_email',
#                 'marital_status', 'spouse_name', 'spouse_phone','client_picture'
#             ]
#         }),
#         ('Client Identification', {
#             'fields': [
#                 'id_type', 'id_number',
#                 'lga_of_origin', 'town_of_origin', 'state_of_origin'
#             ]
#         }),
#         ('Client Bank Details', {
#             'fields': [
#                 'bank_name', 'account_number', 'account_name'
#             ]
#         }),
#         ('Next of Kin', {
#             'fields': ['next_of_kin_name', 'next_of_kin_address', 'next_of_kin_phone']
#         }),
#         ('Pricing & Payment', {
#             'fields': [
#                 'original_price', 'selling_price', 'amount_paid', 'payment_plan'
#             ]
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
                   'selling_price_display', 'amount_paid_display', 'balance_due_display',
                   'development_status_display_admin', 'is_developed')
    
    list_filter = ('is_developed', 'property_type', 'payment_plan', 'marital_status')
    
    search_fields = ('client_name', 'property_item__name', 'reference_number')
    
    fieldsets = [
        ('Property Information', {
            'fields': ['property_type', 'property_item', 'description', 'quantity']
        }),
        ('Client Information', {
            'fields': [
                'client_name', 'client_address', 'client_phone', 'client_email',
                'marital_status', 'spouse_name', 'spouse_phone', 'client_picture'
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
        ('Plot Development Timeline', {
            'fields': [
                'plot_development_start_date', 'plot_development_expiry_date', 
                'is_developed'
            ],
            'description': 'Set development timeline and track completion status'
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
    
    readonly_fields = ('reference_number', 'created_at', 'updated_at')
    
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
    
    def development_status_display_admin(self, obj):
        """Display development status with color coding for admin list"""
        status = obj.development_status_display
        css_class = obj.development_status_class
        
        # Map badge classes to admin-friendly colors
        color_map = {
            'badge-success': '#28a745',  # Green for developed
            'badge-danger': '#dc3545',   # Red for expired
            'badge-warning': '#ffc107',  # Yellow for expiring
            'badge-info': '#17a2b8',     # Blue for valid
            'badge-secondary': '#6c757d' # Gray for no timeline
        }
        
        color = color_map.get(css_class, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    development_status_display_admin.short_description = 'Development Status'
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related('property_item', 'realtor')
    
    # Add custom actions for bulk operations
    actions = ['mark_as_developed', 'mark_as_not_developed']
    
    def mark_as_developed(self, request, queryset):
        """Mark selected properties as developed"""
        updated = queryset.update(is_developed=True)
        self.message_user(
            request,
            f'{updated} property(ies) marked as developed.',
            messages.SUCCESS
        )
    mark_as_developed.short_description = "Mark selected properties as developed"
    
    def mark_as_not_developed(self, request, queryset):
        """Mark selected properties as not developed"""
        updated = queryset.update(is_developed=False)
        self.message_user(
            request,
            f'{updated} property(ies) marked as not developed.',
            messages.SUCCESS
        )
    mark_as_not_developed.short_description = "Mark selected properties as not developed"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'payment_date_display',
        'property_sale_display',
        'client_name_display',
        'realtor_display',
        'amount_display',
        'payment_method_display',
        'reference_display',
        'created_at_display'
    )
    list_filter = ('payment_method', 'payment_date', 'property_sale__realtor')
    search_fields = (
        'property_sale__client_name',
        'property_sale__reference_number',
        'reference',
        'property_sale__realtor__first_name',
        'property_sale__realtor__last_name',
        'notes'
    )
    readonly_fields = ('created_at_display', 'sale_balance_display', 'commissions_created_display')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date', '-id')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('property_sale', 'amount', 'payment_date', 'payment_method')
        }),
        ('Additional Details', {
            'fields': ('reference', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at_display', 'sale_balance_display', 'commissions_created_display'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['find_duplicate_payments', 'recalculate_sale_totals']
    
    def property_sale_display(self, obj):
        """Display property sale reference with link"""
        if obj.property_sale:
            url = f'/vatican123_django_adminxyzx/estate/propertysale/{obj.property_sale.id}/change/'
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url,
                obj.property_sale.reference_number
            )
        return '-'
    property_sale_display.short_description = 'Sale Reference'
    
    def client_name_display(self, obj):
        """Display client name"""
        if obj.property_sale:
            return obj.property_sale.client_name or '-'
        return '-'
    client_name_display.short_description = 'Client'
    
    def realtor_display(self, obj):
        """Display realtor name with link"""
        if obj.property_sale and obj.property_sale.realtor:
            realtor = obj.property_sale.realtor
            # Check if realtor has a valid ID
            if realtor.id is not None:
                url = f'/vatican123_django_adminxyzx/estate/realtor/{realtor.id}/change/'
                return format_html(
                    '<a href="{}" target="_blank">{}</a>',
                    url,
                    realtor.full_name
                )
            else:
                # If no ID, just show the name without link
                return realtor.full_name
        return '-'
    realtor_display.short_description = 'Realtor'
    
    def amount_display(self, obj):
        """Display formatted amount"""
        try:
            amount = float(obj.amount) if obj.amount else 0
            return format_html(
                '<strong style="color: #28a745;">₦{:,.2f}</strong>',
                amount
            )
        except (ValueError, TypeError):
            return format_html('<strong>₦{}</strong>', obj.amount)
    amount_display.short_description = 'Amount'
    
    def payment_method_display(self, obj):
        """Display payment method with badge"""
        method_colors = {
            'Cash': '#6c757d',
            'Bank Transfer': '#007bff',
            'Cheque': '#17a2b8',
            'Card': '#28a745',
        }
        color = method_colors.get(obj.payment_method, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.payment_method
        )
    payment_method_display.short_description = 'Method'
    
    def reference_display(self, obj):
        """Display payment reference"""
        return obj.reference if obj.reference else '-'
    reference_display.short_description = 'Reference'
    
    def payment_date_display(self, obj):
        """Display formatted payment date"""
        if obj.payment_date:
            return obj.payment_date.strftime('%b %d, %Y')
        return '-'
    payment_date_display.short_description = 'Payment Date'
    payment_date_display.admin_order_field = 'payment_date'
    
    def created_at_display(self, obj):
        """Display when record was created"""
        from django.utils import timezone
        if hasattr(obj, 'created_at') and obj.created_at:
            return obj.created_at.strftime('%b %d, %Y %I:%M %p')
        return 'N/A'
    created_at_display.short_description = 'Record Created'
    
    def sale_balance_display(self, obj):
        """Display remaining balance on the sale"""
        if obj.property_sale:
            try:
                balance = float(obj.property_sale.balance_due) if obj.property_sale.balance_due else 0
                if balance > 0:
                    return format_html(
                        '<span style="color: #dc3545;">₦{:,.2f} remaining</span>',
                        balance
                    )
                else:
                    return format_html(
                        '<span style="color: #28a745;">✓ Fully Paid</span>'
                    )
            except (ValueError, TypeError, AttributeError):
                return '-'
        return '-'
    sale_balance_display.short_description = 'Sale Balance'
    
    def commissions_created_display(self, obj):
        """Display commissions created from this payment"""
        from estate.models import Commission
        
        if obj.property_sale:
            try:
                # Find commissions related to this payment
                # This is approximate - we look for commissions created around the same time
                commissions = Commission.objects.filter(
                    property_reference=obj.property_sale.reference_number,
                    description__icontains='payment'
                )
                
                if commissions.exists():
                    total = float(sum(c.amount for c in commissions))
                    return format_html(
                        '{} commission(s) - Total: ₦{:,.2f}',
                        commissions.count(),
                        total
                    )
            except (ValueError, TypeError, AttributeError):
                return 'Error calculating commissions'
        return 'No commissions found'
    commissions_created_display.short_description = 'Commissions Generated'
    
    def find_duplicate_payments(self, request, queryset):
        """Find potential duplicate payments"""
        from collections import defaultdict
        
        duplicates_found = 0
        payment_groups = defaultdict(list)
        
        # Group payments by sale, amount, and date
        for payment in queryset:
            key = (
                payment.property_sale_id,
                str(payment.amount),
                payment.payment_date.date() if payment.payment_date else None
            )
            payment_groups[key].append(payment)
        
        # Find duplicates
        duplicate_ids = []
        for key, payments in payment_groups.items():
            if len(payments) > 1:
                duplicates_found += len(payments) - 1
                duplicate_ids.extend([p.id for p in payments[1:]])
        
        if duplicates_found > 0:
            self.message_user(
                request,
                f'Found {duplicates_found} potential duplicate payment(s). IDs: {duplicate_ids}',
                messages.WARNING
            )
        else:
            self.message_user(
                request,
                'No duplicate payments found in selection.',
                messages.SUCCESS
            )
    find_duplicate_payments.short_description = "🔍 Find duplicate payments"
    
    def recalculate_sale_totals(self, request, queryset):
        """Recalculate property sale totals for selected payments"""
        from estate.models import PropertySale
        from django.db.models import Sum
        
        sales_updated = set()
        
        for payment in queryset:
            if payment.property_sale:
                sale = payment.property_sale
                
                # Recalculate total from all payments
                total_payments = Payment.objects.filter(
                    property_sale=sale
                ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
                
                if sale.amount_paid != total_payments:
                    sale.amount_paid = total_payments
                    sale.save()
                    sales_updated.add(sale.reference_number)
        
        if sales_updated:
            self.message_user(
                request,
                f'Recalculated totals for {len(sales_updated)} sale(s): {", ".join(sales_updated)}',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'All selected payments already have correct totals.',
                messages.INFO
            )
    recalculate_sale_totals.short_description = "🔄 Recalculate sale totals"
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries"""
        return super().get_queryset(request).select_related(
            'property_sale',
            'property_sale__realtor'
        )
    
    
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
    
    def save_model(self, request, obj, form, change):
        # Validate file is present
        if not obj.form_file:
            raise ValidationError("Form file is required!")
        super().save_model(request, obj, form, change)
        
        # Verify ID was assigned
        if obj.id is None:
            raise ValidationError("Form was not saved properly - please try again")
    
    
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