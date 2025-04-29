from django.shortcuts import render,redirect, get_object_or_404


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Realtor, Commission

from django.contrib.auth.forms import PasswordChangeForm                                   # :contentReference[oaicite:0]{index=0}
from django.contrib.auth import update_session_auth_hash 

from django.db.models import Q 



from .models import Property, PropertySale, Payment
from django.http import JsonResponse
from decimal import Decimal,InvalidOperation
from django.utils import timezone

from django.db.models import Sum  # Add this import


# Create your views here.

def home(request):
    return render(request, 'estate/index.html')

def about(request):
    return render(request, 'estate/about.html')

def estates(request):
    return render(request, 'estate/estates.html')

def buildingprojects(request):
    return render(request, 'estate/buildingprojects.html')

def downloadables(request):
    return render(request, 'estate/downloadables.html')


def contact(request):
    return render(request, 'estate/contact.html')


# ====================================ADMIN INTERFACE================================================================================
# ===================================                =================================================================================
@login_required
def userhome(request):
   # Calculate total sales amount (in Naira)
    total_sales_amount = PropertySale.objects.aggregate(Sum('selling_price'))['selling_price__sum'] or Decimal('0')
    
    # Count number of property sales transactions
    total_sales_count = PropertySale.objects.count()
    
    # Count total realtors
    total_realtors = Realtor.objects.count()
    
    # Count paid commissions
    paid_commissions_count = Commission.objects.filter(is_paid=True).count()
    
    # Count unpaid commissions
    unpaid_commissions_count = Commission.objects.filter(is_paid=False).count()
    
    # Calculate total paid commissions amount
    total_paid_commissions = Commission.objects.filter(is_paid=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    # Calculate total unpaid commissions amount
    total_unpaid_commissions = Commission.objects.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    # Format the numbers with appropriate suffixes
    def format_number(number):
        if number >= 1_000_000_000:  # Billions
            return f"₦{number / 1_000_000_000:.1f}B"
        elif number >= 1_000_000:  # Millions
            return f"₦{number / 1_000_000:.1f}M"
        elif number >= 1_000:  # Thousands
            return f"₦{number / 1_000:.1f}K"
        else:
            return f"₦{number:.0f}"
    
    context = {
        'total_sales_amount': format_number(total_sales_amount),
        'total_sales_count': total_sales_count,
        'total_realtors': total_realtors,
        'paid_commissions_count': paid_commissions_count,
        'unpaid_commissions_count': unpaid_commissions_count,
        'total_paid_commissions': format_number(total_paid_commissions),
        'total_unpaid_commissions': format_number(total_unpaid_commissions),
    }
    
    
    return render(request, "user/home.html", context)

@login_required
def profile(request):
    user = request.user
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        # PROFILE UPDATE
        if 'profile_submit' in request.POST:
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name  = request.POST.get('last_name',  user.last_name)
            profile_image   = request.FILES.get('profile_image')
            if profile_image:
                user.image = profile_image
            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')

        # PASSWORD CHANGE
        elif 'password_submit' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()                     # hashes & saves new password :contentReference[oaicite:9]{index=9}  
                update_session_auth_hash(request, user)         # preserve session :contentReference[oaicite:10]{index=10}  
                messages.success(request, "Password changed successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors below.")

    return render(request, 'user/profile.html', {
        'user': user,
        'password_form': password_form,
    })



def signin(request):
    if not request.user.is_authenticated and request.GET.get('next'):
        messages.info(request, "You need to login to access this page.")
        
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # user = authenticate(request, username=username, password=password)
        user = None
        
        if '@' in username:  # Email login case
            user = authenticate(request, username=User.objects.filter(email=username).first().username, password=password)
        else:  # Username login case
            user = authenticate(request, username=username, password=password)
        
        if user is not None:
            
            login(request, user)
            
        
            messages.success(request, "login successful")
            return redirect('user')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "user/signin.html")



    

@login_required
def signout(request):
    logout(request)
    messages.success(request, "logout successful")
    return redirect('signin')


@login_required
def realtors_page(request):
    realtors = Realtor.objects.all()
    context={
        "realtors":realtors
    }
    
    return render(request, "user/realtors_page.html", context )

@login_required
def create_realtor(request):
    """View for creating a new realtor profile"""
    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        account_number = request.POST.get('accnumber')
        bank_name = request.POST.get('bankname')
        address = request.POST.get('address')
        country = request.POST.get('country')
        sponsor_code = request.POST.get('sponsorcode')
        
        # Create new realtor instance
        realtor = Realtor(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            account_number=account_number,
            bank_name=bank_name,
            address=address,
            country=country,
            sponsor_code=sponsor_code
        )
        
        # Handle image upload
        if 'image' in request.FILES:
            realtor.image = request.FILES['image']
            
        # Save the realtor (this will also generate the referral code)
        try:
            realtor.save()
            messages.success(request, f"Realtor profile created successfully! Referral code: {realtor.referral_code}")
            # return redirect('create_realtor', pk=realtor.pk)  # Redirect to detail view or appropriate page
            return redirect('realtor_detail',id=realtor.id)  # Redirect to detail view or appropriate page

        except Exception as e:
            messages.error(request, f"Error creating realtor profile: {str(e)}")
    
    # For GET requests, just render the form
    return render(request, "user/create_realtor.html")  # Replace with your actual template path

@login_required
def realtor_detail(request,id):
    """
    Display detailed information about a realtor, including their commissions,
    direct referrals, and second-level referrals.
    """
    
    realtor = get_object_or_404(Realtor, id=id)
    
    # Get commissions for this realtor
    commissions = Commission.objects.filter(realtor=realtor).order_by('-created_at')
    
    # Get direct referrals (realtors who used this realtor's referral code)
    direct_referrals = Realtor.objects.filter(sponsor=realtor).order_by('-created_at')
    
    # Get second-level referrals (realtors referred by this realtor's direct referrals)
    secondary_referrals = Realtor.objects.filter(
        sponsor__sponsor=realtor
    ).order_by('-created_at')
    
    context = {
        'realtor': realtor,
        'commissions': commissions,
        'direct_referrals': direct_referrals,
        'secondary_referrals': secondary_referrals,
    }
    
    return render(request, "user/realtor_detail.html", context)

# @login_required
# def edit_realtor(request,id):
#     realtor = get_object_or_404(Realtor, id=id)
    
#     if request.method == 'POST':
#         # Extract form data
#         realtor.first_name = request.POST.get('firstname')
#         realtor.last_name = request.POST.get('lastname')
#         realtor.email = request.POST.get('email')
#         realtor.phone = request.POST.get('phone')
#         realtor.account_number = request.POST.get('accnumber')
#         realtor.bank_name = request.POST.get('bankname')
#         realtor.address = request.POST.get('address')
#         realtor.country = request.POST.get('country')
        
#         # Handle image upload
#         if 'image' in request.FILES:
#             realtor.image = request.FILES['image']
            
#         realtor.save()
#         messages.success(request, "Realtor information updated successfully.")
#         return redirect('realtor_detail', id=realtor.id)
    
#     return render(request, 'user/edit_realtor.html', {'realtor': realtor})


@login_required
def edit_realtor(request, id):
    """View for editing an existing realtor profile"""
    realtor = get_object_or_404(Realtor, id=id)
    
    if request.method == 'POST':
        # Extract form data
        realtor.first_name = request.POST.get('firstname')
        realtor.last_name = request.POST.get('lastname')
        realtor.email = request.POST.get('email')
        realtor.phone = request.POST.get('phone')
        realtor.account_number = request.POST.get('accnumber')
        realtor.bank_name = request.POST.get('bankname')
        realtor.address = request.POST.get('address')
        realtor.country = request.POST.get('country')
        
        # Handle status field if your model has it
        if 'status' in request.POST:
            realtor.status = request.POST.get('status')
        
        # Handle bio field if your model has it
        if 'bio' in request.POST:
            realtor.bio = request.POST.get('bio')
        
        # Handle image upload
        if 'image' in request.FILES:
            # New image uploaded
            realtor.image = request.FILES['image']
        elif 'remove_image' in request.POST:
            # Remove existing image
            realtor.image = None
            
        realtor.save()
        messages.success(request, "Realtor information updated successfully.")
        return redirect('realtor_detail', id=realtor.id)
    
    return render(request, 'user/edit_realtor.html', {'realtor': realtor})


# @permission_required('realtors.can_pay_commission', raise_exception=True)
@login_required
def pay_all_commissions(request, realtor_id):
    """Mark all unpaid commissions for a realtor as paid"""
    if request.method == 'POST':
        realtor = get_object_or_404(Realtor, pk=realtor_id)
        unpaid_commissions = Commission.objects.filter(realtor=realtor, is_paid=False)
        
        count = 0
        for commission in unpaid_commissions:
            commission.mark_as_paid()
            count += 1
            
        if count > 0:
            messages.success(request, f"{count} commissions totaling ${realtor.unpaid_commission} have been marked as paid.")
        else:
            messages.info(request, "There were no unpaid commissions to mark as paid.")
            
    return redirect('realtor_detail', id=realtor_id)

            
            
@login_required
def register_property(request):
    """View to register a new property"""
    # Get all states from Property model choices
    states = Property._meta.get_field('location').choices
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        location = request.POST.get('location')
        address = request.POST.get('address')
        
        # Create new property
        property = Property.objects.create(
            name=name,
            description=description,
            location=location,
            address=address
        )
        
        messages.success(request, f'Property "{name}" has been registered successfully!')
        return redirect('property_list')
    
    return render(request, 'user/register_property.html', {
        'states': states
    })

@login_required
def property_list(request):
    """View to display all properties"""
    properties = Property.objects.all().order_by('-created_at')
    
    return render(request, 'user/property_list.html', {
        'properties': properties
    })




# @login_required
# def property_detail(request, property_id):
#     """View to display property details"""
#     property = get_object_or_404(Property, id=property_id)
    
#     # Get all sales for this property - use property_item instead of property
#     sales = PropertySale.objects.filter(property_item=property).order_by('-created_at')
    
#     return render(request, 'user/property_detail.html', {
#         'property': property,
#         'sales': sales  # Uncommented this line as you might need it
#     })
    
    
@login_required
def property_detail(request, property_id):
    """View to display property details with a more comprehensive interface"""
    property = get_object_or_404(Property, id=property_id)
    
    # Get all sales for this property - use property_item instead of property
    sales = PropertySale.objects.filter(property_item=property).order_by('-created_at')
    
    context = {
        'property': property,
        'sales': sales
    }
    
    return render(request, 'user/property_detail.html', context)


@login_required
def edit_property(request, property_id):
    """View for editing an existing property"""
    property = get_object_or_404(Property, id=property_id)
    
    # Get all states from Property model choices for the form dropdown
    states = Property._meta.get_field('location').choices
    
    if request.method == 'POST':
        # Extract form data
        property.name = request.POST.get('name')
        property.description = request.POST.get('description')
        property.location = request.POST.get('location')
        property.address = request.POST.get('address')
        
        # Handle status field if your model has it
        if 'status' in request.POST:
            property.status = request.POST.get('status')
        
        # Handle image upload
        if 'image' in request.FILES:
            # New image uploaded
            property.image = request.FILES['image']
        elif 'remove_image' in request.POST:
            # Remove existing image
            property.image = None
            
        property.save()
        messages.success(request, "Property information updated successfully.")
        return redirect('property_detail', property_id=property.id)
    
    return render(request, 'user/edit_property.html', {
        'property': property,
        'states': states
    })
    
    

@login_required
def register_property_sale(request):
    """View to register a new property sale"""
    properties = Property.objects.all().order_by('name')
    realtors = Realtor.objects.all().order_by('first_name', 'last_name')
    
    if request.method == 'POST':
        # Extract form data
        property_id = request.POST.get('property')
        estate_name = request.POST.get('estate_name')
        property_type = request.POST.get('property_type')
        quantity = request.POST.get('quantity')
        
        client_name = request.POST.get('client_name')
        client_address = request.POST.get('client_address')
        client_phone = request.POST.get('client_phone')
        
        next_of_kin_name = request.POST.get('next_of_kin_name')
        next_of_kin_address = request.POST.get('next_of_kin_address')
        next_of_kin_phone = request.POST.get('next_of_kin_phone')
        
        original_price = request.POST.get('original_price')
        selling_price = request.POST.get('selling_price')
        initial_payment = request.POST.get('initial_payment')
        payment_plan = request.POST.get('payment_plan')
        
        realtor_id = request.POST.get('realtor')
        realtor_commission_percentage = request.POST.get('realtor_commission_percentage')
        sponsor_commission_percentage = request.POST.get('sponsor_commission_percentage')
        upline_commission_percentage = request.POST.get('upline_commission_percentage')
        
        # Get related objects
        property_obj = get_object_or_404(Property, id=property_id)
        realtor = get_object_or_404(Realtor, id=realtor_id)
        
       
        property_sale = PropertySale.objects.create(
            estate_name=estate_name,
            property_type=property_type,
            property_item=property_obj,
            quantity=int(quantity),
            
            client_name=client_name,
            client_address=client_address,
            client_phone=client_phone,
            
            next_of_kin_name=next_of_kin_name,
            next_of_kin_address=next_of_kin_address,
            next_of_kin_phone=next_of_kin_phone,
            
            original_price=Decimal(original_price),
            selling_price=Decimal(selling_price),
            payment_plan=payment_plan,
            
            realtor=realtor,
            realtor_commission_percentage=Decimal(realtor_commission_percentage),
            sponsor_commission_percentage=Decimal(sponsor_commission_percentage),
            upline_commission_percentage=Decimal(upline_commission_percentage)
        )
   
        if float(initial_payment) > 0:
            Payment.objects.create(
                property_sale=property_sale,
                amount=Decimal(initial_payment),
                payment_method='Cash',
                notes='Initial payment at registration'
            )
        
        messages.success(request, f'Property sale registered successfully with reference #{property_sale.reference_number}')
        return redirect('property_sale_detail', id=property_sale.id)
        # return redirect('property_sale_detail', sale_id=property_sale.id)
    
    return render(request, 'user/register_property_sale.html', {
        'properties': properties,
        'realtors': realtors
    })

@login_required
def property_sales_list(request):
    """View to display all property sales"""
    sales = PropertySale.objects.all().order_by('-created_at')
    
    return render(request, 'user/property_sales_list.html', {
        'sales': sales
    })


@login_required
def property_sale_detail(request, id):
    """View details of a property sale and handle new payments"""
    sale = get_object_or_404(PropertySale, pk=id)
    payments = Payment.objects.filter(property_sale=sale).order_by('-payment_date')
    
    # Get balance due directly from the model property
    balance_due = sale.balance_due
    
    # Calculate commissions based on current amount paid
    realtor_commission = (sale.amount_paid * Decimal(sale.realtor_commission_percentage)) / Decimal('100')
    
    sponsor_commission = Decimal('0')
    if sale.realtor.sponsor:
        sponsor_commission = (sale.amount_paid * Decimal(sale.sponsor_commission_percentage)) / Decimal('100')
    
    upline_commission = Decimal('0')
    if sale.realtor.sponsor and sale.realtor.sponsor.sponsor:
        upline_commission = (sale.amount_paid * Decimal(sale.upline_commission_percentage)) / Decimal('100')
    
    # Calculate payment progress percentage using Decimal
    payment_progress_percent = Decimal('0')
    if sale.selling_price > 0:
        payment_progress_percent = (sale.amount_paid * Decimal('100')) / sale.selling_price
        # Round to 2 decimal places for display
        payment_progress_percent = payment_progress_percent.quantize(Decimal('0.01'))
    
    # Handle new payment submission
    if request.method == 'POST':
        # Only process if there's still a balance due
        if balance_due > 0:
            try:
                # Ensure we're working with Decimal from the start
                amount = Decimal(request.POST.get('amount', '0'))
                payment_method = request.POST.get('payment_method', 'Cash')
                reference = request.POST.get('reference', '')
                notes = request.POST.get('notes', '')
                
                # Validate amount is positive
                if amount <= 0:
                    messages.error(request, "Payment amount must be greater than zero.")
                    return redirect('property_sale_detail', id=sale.id)
                
                # Ensure amount doesn't exceed balance due
                if amount > balance_due:
                    amount = balance_due
                    # Format amount for display
                    messages.info(request, f"Payment amount adjusted to ₦{amount.quantize(Decimal('0.01'))} to match remaining balance.")
                
                # Create new payment - this will automatically update the sale's amount_paid in the Payment.save() method
                payment = Payment(
                    property_sale=sale,
                    amount=amount,
                    payment_method=payment_method,
                    reference=reference,
                    notes=notes,
                    payment_date=timezone.now()
                )
                payment.save()
                
                # Refresh the sale object to get updated values after payment
                sale.refresh_from_db()
                
                # Recalculate balance due
                balance_due = sale.balance_due
                
                # Recalculate commissions
                realtor_commission = (sale.amount_paid * Decimal(sale.realtor_commission_percentage)) / Decimal('100')
                
                sponsor_commission = Decimal('0')
                if sale.realtor.sponsor:
                    sponsor_commission = (sale.amount_paid * Decimal(sale.sponsor_commission_percentage)) / Decimal('100')
                
                upline_commission = Decimal('0')
                if sale.realtor.sponsor and sale.realtor.sponsor.sponsor:
                    upline_commission = (sale.amount_paid * Decimal(sale.upline_commission_percentage)) / Decimal('100')
                
                # Recalculate payment progress
                if sale.selling_price > 0:
                    payment_progress_percent = (sale.amount_paid * Decimal('100')) / sale.selling_price
                    payment_progress_percent = payment_progress_percent.quantize(Decimal('0.01'))
                
                messages.success(request, f"Payment of ₦{amount.quantize(Decimal('0.01'))} successfully recorded!")
                
                # Check if payment is now complete
                if balance_due <= 0:
                    messages.success(request, "Congratulations! This property has been fully paid for.")
            except (ValueError, InvalidOperation):
                messages.error(request, "Invalid payment amount. Please enter a valid number.")
        else:
            messages.info(request, "This property has already been fully paid for.")
        
        # Redirect to avoid form resubmission
        return redirect('property_sale_detail', id=sale.id)
    
    context = {
        'sale': sale,
        'payments': payments,
        'realtor_commission': realtor_commission.quantize(Decimal('0.01')),
        'sponsor_commission': sponsor_commission.quantize(Decimal('0.01')),
        'upline_commission': upline_commission.quantize(Decimal('0.01')),
        'payment_progress_percent': payment_progress_percent,
        'balance_due': balance_due.quantize(Decimal('0.01'))
    }
    
    return render(request, 'user/property_sale_detail.html', context)

@login_required
def pay_commission(request, commission_id):
    """Mark a single commission as paid"""
    if request.method == 'POST' and request.user.is_staff:
        commission = get_object_or_404(Commission, pk=commission_id)
        commission.mark_as_paid()
        messages.success(request, f"Commission #{commission_id} has been marked as paid.")
        return redirect('realtor_detail', id=commission.realtor.id)
    return redirect('home')