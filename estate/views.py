from django.shortcuts import render,redirect, get_object_or_404


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Realtor, Commission

from django.contrib.auth.forms import PasswordChangeForm                                   # :contentReference[oaicite:0]{index=0}
from django.contrib.auth import update_session_auth_hash 

from django.db.models import Q 



from .models import Property, PropertySale, Payment, FormUpload, General, EstateImage, Gallery
from django.http import JsonResponse
from decimal import Decimal,InvalidOperation
from django.utils import timezone

from django.db.models import Sum  # Add this import

from django.core.paginator import Paginator


from django.contrib.auth.forms import PasswordResetForm
# from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
# from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm

# Get sales data by month for the current year
from django.db.models.functions import TruncMonth
from datetime import datetime
import json

from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_control
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

import decimal

    

# User = get_user_model()


# Create your views here.
def robots_txt(request):
    return HttpResponse("User-agent: *\nDisallow:", content_type="text/plain")

@cache_control(max_age=2592000, public=True)  # 30 days
def home(request):
    return render(request, 'estate/index.html')


def about(request):
    return render(request, 'estate/about.html')


def estates(request):
    redan_city_images = EstateImage.objects.filter(estate='redan_city')
    canaan_city_images = EstateImage.objects.filter(estate='canaan_city')
    vatican_garden_images = EstateImage.objects.filter(estate='vatican_garden')
    
    context = {
        'redan_city_images': redan_city_images,
        'canaan_city_images': canaan_city_images,
        'vatican_garden_images': vatican_garden_images,
    }
    return render(request, 'estate/estates.html', context)

def buildingprojects(request):
    return render(request, 'estate/buildingprojects.html')

def ishiagu(request):
    return render(request, 'estate/ishiagu.html')

def downloadables(request):
    """View to display all uploaded forms"""
    forms = FormUpload.objects.all().order_by('created_at')
    
    context={
        'forms': forms
    }
    return render(request, 'estate/downloadables.html', context)


def contact(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Validate form data
        if name and email and message:
            try:
                # Compose email
                subject = f'New Contact Form Submission from {name}'
                email_message = f"""
                New contact form submission from Vatican Gardens Projects website:
                
                Name: {name}
                Email: {email}
                
                Message:
                {message}
                
                ---
                This message was sent from the Vatican Gardens Projects contact form.
                """
                
                # Send email
                send_mail(
                    subject=subject,
                    message=email_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['info@vaticanprojects.com'],  # Your business email
                    fail_silently=False,
                )
                
                # Success message
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('contact')
                
            except Exception as e:
                # Error message
                messages.error(request, 'Sorry, there was an error sending your message. Please try again or contact us directly.')
        else:
            # Validation error
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'estate/contact.html')

def realtors_check(request):
    """
    View for realtors to search for their profile using their referral code.
    The view accepts a GET parameter 'referral_code' and returns the matching
    realtor profile if found.
    """
    search_performed = False
    realtor = None
    commissions = None
    direct_referrals = None
    
    if 'referral_code' in request.GET and request.GET.get('referral_code').strip():
        search_performed = True
        referral_code = request.GET.get('referral_code').strip()
        
        # Try to find a realtor with the given referral code
        try:
            realtor = Realtor.objects.get(referral_code=referral_code)
            
            # Get commissions for this realtor
            commissions = Commission.objects.filter(realtor=realtor).order_by('-created_at')
            
            # Get direct referrals (realtors who used this realtor's referral code)
            direct_referrals = Realtor.objects.filter(sponsor=realtor).order_by('-created_at')
            
        except Realtor.DoesNotExist:
            messages.error(request, f"No realtor found with referral code: {referral_code}")
    
    context = {
        'realtor': realtor,
        'search_performed': search_performed,
        'commissions': commissions,
        'direct_referrals': direct_referrals
    }
    
    return render(request, 'estate/realtors_check.html', context)

def gallery_view(request):
    """Display gallery images with pagination"""
    # Get all active gallery images ordered by the order field and creation date
    gallery_images = Gallery.objects.filter(is_active=True).order_by('order', '-created_at')
    
    # Pagination - 12 images per page
    paginator = Paginator(gallery_images, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'gallery_images': page_obj,
        'page_obj': page_obj,
        'total_images': gallery_images.count(),
    }
    
    return render(request, 'estate/gallery.html', context)


# ====================================ADMIN INTERFACE================================================================================
# ===================================                =================================================================================
# @login_required
# def userhome(request):
#    # Calculate total sales amount (in Naira)
#     total_sales_amount = PropertySale.objects.aggregate(Sum('selling_price'))['selling_price__sum'] or Decimal('0')
    
#     # Count number of property sales transactions
#     total_sales_count = PropertySale.objects.count()
    
#     # Count total realtors
#     total_realtors = Realtor.objects.count()
    
#     # Count paid commissions
#     paid_commissions_count = Commission.objects.filter(is_paid=True).count()
    
#     # Count unpaid commissions
#     unpaid_commissions_count = Commission.objects.filter(is_paid=False).count()
    
#     # Calculate total paid commissions amount
#     total_paid_commissions = Commission.objects.filter(is_paid=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
#     # Calculate total unpaid commissions amount
#     total_unpaid_commissions = Commission.objects.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
#     # Format the numbers with appropriate suffixes
#     def format_number(number):
#         if number >= 1_000_000_000:  # Billions
#             return f"₦{number / 1_000_000_000:.1f}B"
#         elif number >= 1_000_000:  # Millions
#             return f"₦{number / 1_000_000:.1f}M"
#         elif number >= 1_000:  # Thousands
#             return f"₦{number / 1_000:.1f}K"
#         else:
#             return f"₦{number:.0f}"
    
#     context = {
#         'total_sales_amount': format_number(total_sales_amount),
#         'total_sales_count': total_sales_count,
#         'total_realtors': total_realtors,
#         'paid_commissions_count': paid_commissions_count,
#         'unpaid_commissions_count': unpaid_commissions_count,
#         'total_paid_commissions': format_number(total_paid_commissions),
#         'total_unpaid_commissions': format_number(total_unpaid_commissions),
#     }
    
    
#     return render(request, "user/home.html", context)


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
   
    # Get sales data by month for the current year
    current_year = datetime.now().year
   
    # Monthly sales data
    monthly_sales = PropertySale.objects.filter(
        created_at__year=current_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('selling_price')
    ).order_by('month')
   
    # Monthly commissions data
    monthly_commissions = Commission.objects.filter(
        created_at__year=current_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
   
    # Prepare chart data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    sales_data = [0] * 12
    commission_data = [0] * 12
   
    for entry in monthly_sales:
        month_idx = entry['month'].month - 1  # Convert to 0-based index
        sales_data[month_idx] = float(entry['total'])
   
    for entry in monthly_commissions:
        month_idx = entry['month'].month - 1  # Convert to 0-based index
        commission_data[month_idx] = float(entry['total'])
    
    # Get top 5 realtors by commission earned
    top_realtors = Realtor.objects.annotate(
        commission_earned=Sum('commissions__amount')
    ).exclude(
        commission_earned=None
    ).order_by('-commission_earned')[:5]
    
    top_realtors_data = []
    for realtor in top_realtors:
        top_realtors_data.append({
            'name': realtor.full_name,
            'commission': float(realtor.commission_earned or 0)
        })
   
    # Format data for JavaScript
    chart_data = {
        'months': months,
        'sales': sales_data,
        'commissions': commission_data,
        'topRealtors': top_realtors_data
    }
   
    context = {
        'total_sales_amount': format_number(total_sales_amount),
        'total_sales_count': total_sales_count,
        'total_realtors': total_realtors,
        'paid_commissions_count': paid_commissions_count,
        'unpaid_commissions_count': unpaid_commissions_count,
        'total_paid_commissions': format_number(total_paid_commissions),
        'total_unpaid_commissions': format_number(total_unpaid_commissions),
        'chart_data': json.dumps(chart_data),
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
    """
    View for displaying realtors with search functionality and pagination.
    Allows searching by name, referral code, phone number, etc.
    """
    # Get search parameter from the request
    search_query = request.GET.get('search', '')
    
    # Start with all realtors
    realtors = Realtor.objects.all()
    
    # Apply search filter if a search query is provided
    if search_query:
        realtors = realtors.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(referral_code__icontains=search_query) | 
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Order the results
    realtors = realtors.order_by('first_name', 'last_name')
    
    # Paginate the results
    paginator = Paginator(realtors, 10)  # Show 10 realtors per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        "realtors": page_obj,  # Pass the paginated object instead of the full queryset
        "search_query": search_query,  # Pass the search query back to the template
        "page_obj": page_obj,  # Pagination object for creating pagination controls
        "paginator": paginator,  # The paginator object itself
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


@login_required
def delete_realtor(request, id):
    """
    View to delete a realtor after confirmation
    """
    # Get the realtor object or return 404
    realtor = get_object_or_404(Realtor, id=id)
    
    # Check if there are commissions associated with this realtor
    has_commissions = Commission.objects.filter(realtor=realtor).exists()
    
    # Check if there are property sales associated with this realtor
    has_sales = PropertySale.objects.filter(realtor=realtor).exists()
    
    # If this is a POST request, delete the realtor
    if request.method == "POST":
        # Check if realtor can be safely deleted
        if has_commissions or has_sales:
            messages.warning(request, 
                f"Cannot delete '{realtor.first_name} {realtor.last_name}' because they have associated commissions or sales records.")
        else:
            realtor_name = f"{realtor.first_name} {realtor.last_name}"  # Store name before deletion
            realtor.delete()
            messages.success(request, f"Realtor '{realtor_name}' has been deleted successfully.")
        
    # Redirect back to the realtors list
    return redirect('realtors_page')


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
def delete_property(request, property_id):
    """
    View to delete a property after confirmation
    """
    # Get the property object or return 404
    property_obj = get_object_or_404(Property, id=property_id)
    
    # Remove the user check for now, or replace with appropriate check
    # if property_obj.user != request.user:
    #     messages.error(request, "You don't have permission to delete this property.")
    #     return redirect('property_list')
    
    # Check if there are any sales associated with this property
    if property_obj.sales.exists():
        messages.warning(request, 
            f"Cannot delete '{property_obj.name}' because it has associated sales records.")
        return redirect('property_list')
    
    # If this is a POST request, delete the property
    if request.method == "POST":
        property_name = property_obj.name  # Store name before deletion
        property_obj.delete()
        messages.success(request, f"Property '{property_name}' has been deleted successfully.")
        
    # Redirect back to the property list
    return redirect('property_list')
    

# @login_required
# def register_property_sale(request):
#     """View to register a new property sale"""
#     properties = Property.objects.all().order_by('name')
#     realtors = Realtor.objects.all().order_by('first_name', 'last_name')
    
#     if request.method == 'POST':
#         # Extract form data
#         property_id = request.POST.get('property')
#         description = request.POST.get('description')
#         property_type = request.POST.get('property_type')
#         quantity = request.POST.get('quantity')
        
#         client_name = request.POST.get('client_name')
#         client_address = request.POST.get('client_address')
#         client_phone = request.POST.get('client_phone')
        
#         next_of_kin_name = request.POST.get('next_of_kin_name')
#         next_of_kin_address = request.POST.get('next_of_kin_address')
#         next_of_kin_phone = request.POST.get('next_of_kin_phone')
        
#         original_price = request.POST.get('original_price')
#         selling_price = request.POST.get('selling_price')
#         initial_payment = request.POST.get('initial_payment')
#         payment_plan = request.POST.get('payment_plan')
        
#         realtor_id = request.POST.get('realtor')
#         realtor_commission_percentage = request.POST.get('realtor_commission_percentage')
#         sponsor_commission_percentage = request.POST.get('sponsor_commission_percentage')
#         upline_commission_percentage = request.POST.get('upline_commission_percentage')
        
#         # Get related objects
#         property_obj = get_object_or_404(Property, id=property_id)
#         realtor = get_object_or_404(Realtor, id=realtor_id)
        
       
#         property_sale = PropertySale.objects.create(
#             description=description,
#             property_type=property_type,
#             property_item=property_obj,
#             quantity=int(quantity),
            
#             client_name=client_name,
#             client_address=client_address,
#             client_phone=client_phone,
            
#             next_of_kin_name=next_of_kin_name,
#             next_of_kin_address=next_of_kin_address,
#             next_of_kin_phone=next_of_kin_phone,
            
#             original_price=Decimal(original_price),
#             selling_price=Decimal(selling_price),
#             payment_plan=payment_plan,
            
#             realtor=realtor,
#             realtor_commission_percentage=Decimal(realtor_commission_percentage),
#             sponsor_commission_percentage=Decimal(sponsor_commission_percentage),
#             upline_commission_percentage=Decimal(upline_commission_percentage)
#         )
   
#         if float(initial_payment) > 0:
#             Payment.objects.create(
#                 property_sale=property_sale,
#                 amount=Decimal(initial_payment),
#                 payment_method='Cash',
#                 notes='Initial payment at registration'
#             )
        
#         messages.success(request, f'Property sale registered successfully with reference #{property_sale.reference_number}')
#         return redirect('property_sale_detail', id=property_sale.id)
#         # return redirect('property_sale_detail', sale_id=property_sale.id)
    
#     return render(request, 'user/register_property_sale.html', {
#         'properties': properties,
#         'realtors': realtors
#     })



# @login_required
# def register_property_sale(request):
#     """View to register a new property sale"""
#     properties = Property.objects.all().order_by('name')
#     realtors = Realtor.objects.all().order_by('first_name', 'last_name')
    
#     if request.method == 'POST':
#         # Extract basic property information
#         property_id = request.POST.get('property')
#         description = request.POST.get('description')
#         property_type = request.POST.get('property_type')
#         quantity = request.POST.get('quantity')
        
#         # Extract client information
#         client_name = request.POST.get('client_name')
#         client_address = request.POST.get('client_address')
#         client_phone = request.POST.get('client_phone')
#         client_email = request.POST.get('client_email')
#         marital_status = request.POST.get('marital_status')
#         spouse_name = request.POST.get('spouse_name', '')
#         spouse_phone = request.POST.get('spouse_phone', '')
        
#         # Extract client identification
#         id_type = request.POST.get('id_type')
#         id_number = request.POST.get('id_number')
        
#         # Extract client origin
#         lga_of_origin = request.POST.get('lga_of_origin')
#         town_of_origin = request.POST.get('town_of_origin')
#         state_of_origin = request.POST.get('state_of_origin')
        
#         # Extract client bank details
#         bank_name = request.POST.get('bank_name')
#         account_number = request.POST.get('account_number')
#         account_name = request.POST.get('account_name')
        
#         # Extract next of kin information
#         next_of_kin_name = request.POST.get('next_of_kin_name')
#         next_of_kin_address = request.POST.get('next_of_kin_address')
#         next_of_kin_phone = request.POST.get('next_of_kin_phone')
        
#         # Extract financial information
#         original_price = request.POST.get('original_price')
#         selling_price = request.POST.get('selling_price')
#         initial_payment = request.POST.get('initial_payment')
#         payment_plan = request.POST.get('payment_plan')
        
#         # Extract realtor and commission information
#         realtor_id = request.POST.get('realtor')
#         realtor_commission_percentage = request.POST.get('realtor_commission_percentage')
#         sponsor_commission_percentage = request.POST.get('sponsor_commission_percentage')
#         upline_commission_percentage = request.POST.get('upline_commission_percentage')
        
#         # Get related objects
#         property_obj = get_object_or_404(Property, id=property_id)
#         realtor = get_object_or_404(Realtor, id=realtor_id)
        
#         # Create the property sale object with all fields
#         property_sale = PropertySale.objects.create(
#             description=description,
#             property_type=property_type,
#             property_item=property_obj,
#             quantity=int(quantity),
            
#             client_name=client_name,
#             client_address=client_address,
#             client_phone=client_phone,
#             client_email=client_email,
#             marital_status=marital_status,
#             spouse_name=spouse_name,
#             spouse_phone=spouse_phone,
            
#             id_type=id_type,
#             id_number=id_number,
            
#             lga_of_origin=lga_of_origin,
#             town_of_origin=town_of_origin,
#             state_of_origin=state_of_origin,
            
#             bank_name=bank_name,
#             account_number=account_number,
#             account_name=account_name,
            
#             next_of_kin_name=next_of_kin_name,
#             next_of_kin_address=next_of_kin_address,
#             next_of_kin_phone=next_of_kin_phone,
            
#             original_price=Decimal(original_price),
#             selling_price=Decimal(selling_price),
#             payment_plan=payment_plan,
            
#             realtor=realtor,
#             realtor_commission_percentage=Decimal(realtor_commission_percentage),
#             sponsor_commission_percentage=Decimal(sponsor_commission_percentage),
#             upline_commission_percentage=Decimal(upline_commission_percentage)
#         )
        
#         # Create initial payment if provided
#         if float(initial_payment) > 0:
#             # Update the amount_paid field first
#             property_sale.amount_paid = Decimal(initial_payment)
#             property_sale.save()
            
#             # Create the payment record
#             Payment.objects.create(
#                 property_sale=property_sale,
#                 amount=Decimal(initial_payment),
#                 payment_method='Cash',
#                 notes='Initial payment at registration'
#             )
        
#         messages.success(request, f'Property sale registered successfully with reference #{property_sale.reference_number}')
#         return redirect('property_sale_detail', id=property_sale.id)
    
#     return render(request, 'user/register_property_sale.html', {
#         'properties': properties,
#         'realtors': realtors
#     })

@login_required
def register_property_sale(request):
    """View to register a new property sale"""
    properties = Property.objects.all().order_by('name')
    realtors = Realtor.objects.all().order_by('first_name', 'last_name')
    
    if request.method == 'POST':
        try:
            # Extract basic property information
            property_id = request.POST.get('property')
            description = request.POST.get('description')
            property_type = request.POST.get('property_type')
            quantity = request.POST.get('quantity')
            
            # Extract client information
            client_name = request.POST.get('client_name')
            client_address = request.POST.get('client_address')
            client_phone = request.POST.get('client_phone')
            client_email = request.POST.get('client_email')
            marital_status = request.POST.get('marital_status')
            spouse_name = request.POST.get('spouse_name', '')
            spouse_phone = request.POST.get('spouse_phone', '')
            
            # Extract client identification
            id_type = request.POST.get('id_type')
            id_number = request.POST.get('id_number')
            
            # Extract client origin
            lga_of_origin = request.POST.get('lga_of_origin')
            town_of_origin = request.POST.get('town_of_origin')
            state_of_origin = request.POST.get('state_of_origin')
            
            # Extract client bank details
            bank_name = request.POST.get('bank_name')
            account_number = request.POST.get('account_number')
            account_name = request.POST.get('account_name')
            
            # Extract next of kin information
            next_of_kin_name = request.POST.get('next_of_kin_name')
            next_of_kin_address = request.POST.get('next_of_kin_address')
            next_of_kin_phone = request.POST.get('next_of_kin_phone')
            
            # Extract financial information
            original_price = request.POST.get('original_price')
            selling_price = request.POST.get('selling_price')
            initial_payment = request.POST.get('initial_payment')
            payment_plan = request.POST.get('payment_plan')
            
            # Extract realtor and commission information
            realtor_id = request.POST.get('realtor')
            realtor_commission_percentage = request.POST.get('realtor_commission_percentage')
            sponsor_commission_percentage = request.POST.get('sponsor_commission_percentage')
            upline_commission_percentage = request.POST.get('upline_commission_percentage')
            
            # Helper function to safely convert to Decimal
            def safe_decimal_conversion(value, field_name, default='0.00'):
                if value is None or str(value).strip() == '':
                    return Decimal(default)
                try:
                    cleaned_value = str(value).strip()
                    return Decimal(cleaned_value)
                except (ValueError, decimal.InvalidOperation) as e:
                    messages.error(request, f'Invalid value for {field_name}: "{value}". Please enter a valid number.')
                    raise ValueError(f'Invalid {field_name} value')
            
            # Validate and convert decimal fields
            try:
                original_price_decimal = safe_decimal_conversion(original_price, 'original price')
                selling_price_decimal = safe_decimal_conversion(selling_price, 'selling price')
                initial_payment_decimal = safe_decimal_conversion(initial_payment, 'initial payment', '0.00')
                realtor_commission_decimal = safe_decimal_conversion(realtor_commission_percentage, 'realtor commission percentage', '0.00')
                sponsor_commission_decimal = safe_decimal_conversion(sponsor_commission_percentage, 'sponsor commission percentage', '0.00')
                upline_commission_decimal = safe_decimal_conversion(upline_commission_percentage, 'upline commission percentage', '0.00')
            except ValueError:
                # Error message already added by safe_decimal_conversion
                return render(request, 'user/register_property_sale.html', {
                    'properties': properties,
                    'realtors': realtors
                })
            
            # Validate quantity
            try:
                quantity_int = int(quantity) if quantity else 1
                if quantity_int <= 0:
                    messages.error(request, 'Quantity must be a positive number.')
                    return render(request, 'user/register_property_sale.html', {
                        'properties': properties,
                        'realtors': realtors
                    })
            except (ValueError, TypeError):
                messages.error(request, 'Invalid quantity value. Please enter a valid number.')
                return render(request, 'user/register_property_sale.html', {
                    'properties': properties,
                    'realtors': realtors
                })
            
            # Get related objects
            property_obj = get_object_or_404(Property, id=property_id)
            realtor = get_object_or_404(Realtor, id=realtor_id)
            
            # Create the property sale object with all fields
            property_sale = PropertySale.objects.create(
                description=description,
                property_type=property_type,
                property_item=property_obj,
                quantity=quantity_int,
                
                client_name=client_name,
                client_address=client_address,
                client_phone=client_phone,
                client_email=client_email,
                marital_status=marital_status,
                spouse_name=spouse_name,
                spouse_phone=spouse_phone,
                
                id_type=id_type,
                id_number=id_number,
                
                lga_of_origin=lga_of_origin,
                town_of_origin=town_of_origin,
                state_of_origin=state_of_origin,
                
                bank_name=bank_name,
                account_number=account_number,
                account_name=account_name,
                
                next_of_kin_name=next_of_kin_name,
                next_of_kin_address=next_of_kin_address,
                next_of_kin_phone=next_of_kin_phone,
                
                original_price=original_price_decimal,
                selling_price=selling_price_decimal,
                payment_plan=payment_plan,
                
                realtor=realtor,
                realtor_commission_percentage=realtor_commission_decimal,
                sponsor_commission_percentage=sponsor_commission_decimal,
                upline_commission_percentage=upline_commission_decimal
            )
            
            # Create initial payment if provided
            if initial_payment_decimal > 0:
                # Update the amount_paid field first
                property_sale.amount_paid = initial_payment_decimal
                property_sale.save()
                
                # Create the payment record
                Payment.objects.create(
                    property_sale=property_sale,
                    amount=initial_payment_decimal,
                    payment_method='Cash',
                    notes='Initial payment at registration'
                )
            
            messages.success(request, f'Property sale registered successfully with reference #{property_sale.reference_number}')
            return redirect('property_sale_detail', id=property_sale.id)
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error in register_property_sale: {str(e)}')
            
            messages.error(request, 'An error occurred while registering the property sale. Please check your input and try again.')
            return render(request, 'user/register_property_sale.html', {
                'properties': properties,
                'realtors': realtors
            })
    
    return render(request, 'user/register_property_sale.html', {
        'properties': properties,
        'realtors': realtors
    })

@login_required
def property_sales_list(request):
    """View to display all property sales"""
    all_sales = PropertySale.objects.all().order_by('-created_at')
    paginator = Paginator(all_sales, 20)            # 20 sales per page
    page_number = request.GET.get('page', 1)        # get ?page= from URL, default to 1
    sales = paginator.get_page(page_number) 
    # sales = PropertySale.objects.all().order_by('-created_at')
    
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







# =============================================================================


@login_required
def frontend_extras(request):
    """Main view for Frontend Extras dashboard"""
    return render(request, "user/frontend_extras.html")

@login_required
def upload_form(request):
    """View for uploading a new form"""
    # Get 5 most recent forms for display
    recent_forms = FormUpload.objects.all().order_by('-created_at')[:5]
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        form_file = request.FILES.get('form_file')
        
        if not form_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('upload_form')
        
        # Create new form upload
        form_upload = FormUpload(
            name=name,
            description=description,
            form_file=form_file
        )
        form_upload.save()
        
        messages.success(request, f"Form '{name}' has been uploaded successfully!")
        return redirect('forms_list')
    
    return render(request, "user/forms_upload.html", {
        'recent_forms': recent_forms
    })

@login_required
def forms_list(request):
    """View to display all uploaded forms"""
    forms = FormUpload.objects.all().order_by('-created_at')
    
    return render(request, "user/forms_list.html", {
        'forms': forms
    })

@login_required
def edit_form(request, form_id):
    """View for editing an existing form"""
    form = get_object_or_404(FormUpload, id=form_id)
    
    if request.method == 'POST':
        # Extract form data
        form.name = request.POST.get('name')
        form.description = request.POST.get('description')
        
        # Handle file upload if new file is provided
        if 'form_file' in request.FILES:
            form.form_file = request.FILES['form_file']
            
        form.save()
        messages.success(request, f"Form '{form.name}' updated successfully.")
        return redirect('forms_list')
    
    return render(request, 'user/edit_form.html', {'form': form})

@login_required
def delete_form(request, form_id):
    """View for deleting a form"""
    if request.method == 'POST':
        form = get_object_or_404(FormUpload, id=form_id)
        form_name = form.name
        form.delete()
        messages.success(request, f"Form '{form_name}' has been deleted.")
    
    return redirect('forms_list')




@login_required
def property_sale_invoice(request, sale_id):
    """
    View for displaying and printing a property sale invoice
    """
    sale = get_object_or_404(PropertySale, id=sale_id)
    payments = Payment.objects.filter(property_sale=sale).order_by('-payment_date')
    
    
    
    # Calculate balance due
    balance_due = sale.selling_price - sale.amount_paid
    settings, created = General.objects.get_or_create(id=1)

    
    context = {
        'sale': sale,
        'payments': payments,
        'balance_due': balance_due,
        'now': timezone.now(),
        # 'settings':General.objects.all()
        'settings':settings
        # **company_info,
    }
    
    return render(request, 'user/property_sale_invoice.html', context)




@login_required
def commissions_list(request):
    """View to display all commissions with search and filtering"""
    # Initialize query
    commissions = Commission.objects.all().order_by('-created_at')
    
    # Search parameters
    search_query = request.GET.get('search', '')
    payment_status = request.GET.get('payment_status', '')
    realtor_id = request.GET.get('realtor_id', '')
    property_ref = request.GET.get('property_ref', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    # In your view function
    realtor_status = request.GET.get('realtor_status', '')

# Apply the filter if realtor_status is provided



    
    # Apply filters
    if search_query:
        # Search by reference number, property reference, or realtor name
        commissions = commissions.filter(
            Q(property_reference__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(realtor__first_name__icontains=search_query) |
            Q(realtor__last_name__icontains=search_query)
        )
    
    if payment_status:
        is_paid = payment_status == 'paid'
        commissions = commissions.filter(is_paid=is_paid)
    
    if realtor_id:
        commissions = commissions.filter(realtor_id=realtor_id)
        
    if property_ref:
        commissions = commissions.filter(property_reference__icontains=property_ref)
    
    if date_from:
        commissions = commissions.filter(created_at__gte=date_from)
    
    if date_to:
        commissions = commissions.filter(created_at__lte=date_to)
    
    if realtor_status:
        commissions = commissions.filter(realtor__status=realtor_status)
    
    # Calculate summary statistics
    total_commissions = commissions.aggregate(Sum('amount'))['amount__sum'] or 0
    paid_commissions = commissions.filter(is_paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
    unpaid_commissions = commissions.filter(is_paid=False).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get all realtors for the filter dropdown
    realtors = Realtor.objects.all().order_by('first_name', 'last_name')
    
    # Pagination
    paginator = Paginator(commissions, 20)  # Show 20 commissions per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_commissions': total_commissions,
        'paid_commissions': paid_commissions,
        'unpaid_commissions': unpaid_commissions,
        'realtors': realtors,
        'search_query': search_query,
        'payment_status': payment_status,
        'property_ref': property_ref,
        'realtor_id': int(realtor_id) if realtor_id and realtor_id.isdigit() else None,
        'date_from': date_from,
        'date_to': date_to,
        # Pass it to the template context
        'realtor_status' : realtor_status
    }
    
    return render(request, 'user/commissions_list.html', context)


# @login_required
# def unpaid_commissions_print(request):
#     """View to display unpaid commissions in a printable format"""
#     # Get all unpaid commissions with related data
#     unpaid_commissions = Commission.objects.filter(
#         is_paid=False
#     ).select_related(
#         'realtor'
#     ).order_by('realtor__last_name', 'realtor__first_name', '-created_at')
    
#     # Get property sales data for property names
#     property_sales = {}
#     for commission in unpaid_commissions:
#         if commission.property_reference:
#             try:
#                 sale = PropertySale.objects.select_related('property_item').get(
#                     reference_number=commission.property_reference
#                 )
#                 property_sales[commission.property_reference] = sale
#             except PropertySale.DoesNotExist:
#                 property_sales[commission.property_reference] = None
    
#     from django.db import models

#     # Calculate totals
#     total_unpaid_amount = unpaid_commissions.aggregate(
#         total=models.Sum('amount')
#     )['total'] or 0
    
#     # Group commissions by realtor for better organization
#     commissions_by_realtor = {}
#     for commission in unpaid_commissions:
#         realtor_id = commission.realtor.id
#         if realtor_id not in commissions_by_realtor:
#             commissions_by_realtor[realtor_id] = {
#                 'realtor': commission.realtor,
#                 'commissions': [],
#                 'total': 0
#             }
#         commissions_by_realtor[realtor_id]['commissions'].append(commission)
#         commissions_by_realtor[realtor_id]['total'] += commission.amount
    
#     context = {
#         'unpaid_commissions': unpaid_commissions,
#         'commissions_by_realtor': commissions_by_realtor,
#         'property_sales': property_sales,
#         'total_unpaid_amount': total_unpaid_amount,
#         'total_realtors': len(commissions_by_realtor),
#         'total_commissions_count': unpaid_commissions.count(),
#         'print_date': timezone.now(),
#     }
    
#     return render(request, 'user/unpaid_commissions_print.html', context)



@login_required
def unpaid_commissions_print(request):
    """View to display unpaid commissions in a printable format"""
    # Get all unpaid commissions with related data
    unpaid_commissions = Commission.objects.filter(
        is_paid=False
    ).select_related(
        'realtor'
    ).order_by('realtor__last_name', 'realtor__first_name', '-created_at')
    
    # Get property sales data for property names
    property_sales = {}
    for commission in unpaid_commissions:
        if commission.property_reference:
            try:
                sale = PropertySale.objects.select_related('property_item').get(
                    reference_number=commission.property_reference
                )
                property_sales[commission.property_reference] = sale
            except PropertySale.DoesNotExist:
                property_sales[commission.property_reference] = None
    
    from django.db import models

    # Calculate totals
    total_unpaid_amount = unpaid_commissions.aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    # Group commissions by realtor for better organization
    commissions_by_realtor = {}
    for commission in unpaid_commissions:
        realtor_id = commission.realtor.id
        if realtor_id not in commissions_by_realtor:
            commissions_by_realtor[realtor_id] = {
                'realtor': commission.realtor,
                'commissions': [],
                'total': 0
            }
        commissions_by_realtor[realtor_id]['commissions'].append(commission)
        commissions_by_realtor[realtor_id]['total'] += commission.amount
    
    context = {
        'unpaid_commissions': unpaid_commissions,
        'commissions_by_realtor': commissions_by_realtor,
        'property_sales': property_sales,
        'total_unpaid_amount': total_unpaid_amount,
        'total_realtors': len(commissions_by_realtor),
        'total_commissions_count': unpaid_commissions.count(),
        'print_date': timezone.now(),
    }
    
    return render(request, 'user/unpaid_commissions_print.html', context)

@login_required
def realtor_unpaid_commissions_print(request, realtor_id):
    """View to display unpaid commissions for a specific realtor in a printable format"""
    # Get the specific realtor
    realtor = get_object_or_404(Realtor, id=realtor_id)
    
    # Get unpaid commissions for this specific realtor
    unpaid_commissions = Commission.objects.filter(
        realtor=realtor,
        is_paid=False
    ).order_by('-created_at')
    
    # Get property sales data for property names
    property_sales = {}
    for commission in unpaid_commissions:
        if commission.property_reference:
            try:
                sale = PropertySale.objects.select_related('property_item').get(
                    reference_number=commission.property_reference
                )
                property_sales[commission.property_reference] = sale
            except PropertySale.DoesNotExist:
                property_sales[commission.property_reference] = None
    
    from django.db import models
    
    # Calculate total unpaid amount for this realtor
    total_unpaid_amount = unpaid_commissions.aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    context = {
        'realtor': realtor,
        'unpaid_commissions': unpaid_commissions,
        'property_sales': property_sales,
        'total_unpaid_amount': total_unpaid_amount,
        'print_date': timezone.now(),
    }
    
    return render(request, 'user/realtor_unpaid_commissions_print.html', context)



# =============================================================================================
# ==================================Password reset===============================
def password_reset_request(request):
    """
    View for handling password reset requests
    """
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "user/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Vatican Garden Estates',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@vaticangarden.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("password_reset_done")
            else:
                messages.error(request, "No account found with that email address.")
                return redirect("password_reset")
    else:
        password_reset_form = PasswordResetForm()
    
    return render(request, "user/password_reset.html", {"password_reset_form": password_reset_form})

def password_reset_done(request):
    """
    View shown after password reset request is processed
    """
    return render(request, "user/password_reset_done.html")

def password_reset_confirm(request, uidb64, token):
    """
    View for confirming password reset and setting new password
    """
    from django.utils.http import urlsafe_base64_decode
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and log in now.")
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'user/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "The password reset link was invalid, possibly because it has already been used. Please request a new password reset.")
        return redirect('signin')

def password_reset_complete(request):
    """
    View shown after password has been successfully reset
    """
    return render(request, "user/password_reset_complete.html")



@login_required
def general_settings(request):
    """
    View to handle displaying and updating general settings
    """
    # Get or create general settings object (assuming only one instance exists)
    settings, created = General.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        # Update settings with form data
        settings.company_bank_name = request.POST.get('bank_name')
        settings.company_account_name = request.POST.get('account_name')  # Note: there's a typo in your model (ame not name)
        settings.company_account_number = request.POST.get('account_number')
        
        # Save the settings
        settings.save()
        
        # Add success message
        messages.success(request, 'Settings updated successfully!')
        
        # Redirect to the same page to prevent form resubmission
        return redirect('general_settings')
    
    # Prepare context for template rendering
    context = {
        'settings': settings,
        'page_title': 'General Settings'
    }
    
    return render(request, 'user/general_settings.html', context)



# Add this function to your views.py

def custom_404_view(request, exception):
    """
    Custom 404 error handler that renders our 404.html template
    """
    return render(request, 'user/404.html', status=404)

# ========================================================================================================




@login_required
def estate_images_list(request):
    """Display all estate images organized by estate type"""
    redan_city_images = EstateImage.objects.filter(estate='redan_city')
    canaan_city_images = EstateImage.objects.filter(estate='canaan_city')
    vatican_garden_images = EstateImage.objects.filter(estate='vatican_garden')
    
    context = {
        'redan_city_images': redan_city_images,
        'canaan_city_images': canaan_city_images,
        'vatican_garden_images': vatican_garden_images,
    }
    
    return render(request, 'user/estate_images_list.html', context)


@login_required
def add_estate_image(request):
    """Add a new estate image"""
    if request.method == 'POST':
        estate = request.POST.get('estate')
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order', 0)
        is_active = 'is_active' in request.POST
        
        # Validate estate type
        valid_estates = ['redan_city', 'canaan_city', 'vatican_garden']
        if estate not in valid_estates:
            messages.error(request, "Invalid estate type selected.")
            return redirect('estate_images_list')
        
        # Check if image file was uploaded
        if 'image' not in request.FILES:
            messages.error(request, "Please select an image to upload.")
            return redirect('estate_images_list')
        
        # Create new estate image
        image = EstateImage(
            estate=estate,
            title=title,
            description=description,
            image=request.FILES['image'],
            order=order,
            is_active=is_active
        )
        image.save()
        
        messages.success(request, f"Image '{title}' added successfully to {dict(EstateImage.ESTATE_CHOICES)[estate]}.")
        return redirect('estate_images_list')
    
    # If not POST, redirect to list view
    return redirect('estate_images_list')


@login_required
def edit_estate_image(request):
    """Edit an existing estate image"""
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        image = get_object_or_404(EstateImage, id=image_id)
        
        # Update fields
        image.title = request.POST.get('title')
        image.description = request.POST.get('description')
        image.order = request.POST.get('order', 0)
        image.is_active = 'is_active' in request.POST
        
        # Update image file if provided
        if 'image' in request.FILES and request.FILES['image']:
            image.image = request.FILES['image']
        
        image.save()
        
        messages.success(request, f"Image '{image.title}' updated successfully.")
        return redirect('estate_images_list')
    
    # If not POST, redirect to list view
    return redirect('estate_images_list')


@login_required
def delete_estate_image(request):
    """Delete an estate image"""
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        image = get_object_or_404(EstateImage, id=image_id)
        estate_name = image.get_estate_display()
        title = image.title
        
        image.delete()
        
        messages.success(request, f"Image '{title}' from {estate_name} deleted successfully.")
    
    return redirect('estate_images_list')


# ----------------==================================-----------------------------------

@login_required
@require_http_methods(["POST"])
def toggle_realtor_status(request, realtor_id):
    """
    Toggle realtor status between regular and executive.
    Only staff members can access this view.
    """
    realtor = get_object_or_404(Realtor, id=realtor_id)
    
    # Store the old status for the success message
    old_status = realtor.status_display
    
    # Toggle status
    if realtor.status == 'regular':
        realtor.promote_to_executive()
        new_status = 'Executive'
        message = f'{realtor.full_name} has been promoted to Executive Realtor! 👑'
        message_tag = 'success'
    else:
        realtor.demote_to_regular()
        new_status = 'Regular'
        message = f'{realtor.full_name} has been changed to Regular Realtor.'
        message_tag = 'info'
    
    # Add success message
    messages.add_message(request, messages.SUCCESS if message_tag == 'success' else messages.INFO, message)
    
    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'is_executive': realtor.is_executive,
            'message': message
        })
    
    # Redirect back to the realtor detail page
    return redirect('realtor_detail', id=realtor.id)


@login_required
@require_http_methods(["POST"])
def bulk_update_realtor_status(request):
    """
    Bulk update multiple realtors' status.
    Expects POST data with realtor_ids and target_status.
    """
    realtor_ids = request.POST.getlist('realtor_ids')
    target_status = request.POST.get('target_status')
    
    if not realtor_ids or target_status not in ['regular', 'executive']:
        messages.error(request, 'Invalid request parameters.')
        return redirect('realtor_list')  # Adjust to your realtor list URL
    
    realtors = Realtor.objects.filter(id__in=realtor_ids)
    updated_count = 0
    
    for realtor in realtors:
        if target_status == 'executive' and realtor.status == 'regular':
            realtor.promote_to_executive()
            updated_count += 1
        elif target_status == 'regular' and realtor.status == 'executive':
            realtor.demote_to_regular()
            updated_count += 1
    
    if updated_count > 0:
        status_name = 'Executive' if target_status == 'executive' else 'Regular'
        messages.success(request, f'{updated_count} realtor(s) have been updated to {status_name} status.')
    else:
        messages.info(request, 'No realtors were updated.')
    
    return redirect('realtor_list')  # Adjust to your realtor list URL



# Optional: API endpoint for AJAX status updates
def realtor_status_api(request, realtor_id):
    """
    API endpoint for realtor status operations.
    GET: Return current status
    POST: Update status
    """
    realtor = get_object_or_404(Realtor, id=realtor_id)
    
    if request.method == 'GET':
        return JsonResponse({
            'realtor_id': realtor.id,
            'full_name': realtor.full_name,
            'status': realtor.status,
            'status_display': realtor.status_display,
            'is_executive': realtor.is_executive,
        })
    
    elif request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status not in ['regular', 'executive']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
        
        if new_status != realtor.status:
            old_status = realtor.status_display
            
            if new_status == 'executive':
                realtor.promote_to_executive()
                message = f'{realtor.full_name} promoted to Executive! 👑'
            else:
                realtor.demote_to_regular()
                message = f'{realtor.full_name} changed to Regular Realtor.'
            
            return JsonResponse({
                'success': True,
                'old_status': old_status,
                'new_status': realtor.status_display,
                'is_executive': realtor.is_executive,
                'message': message
            })
        
        return JsonResponse({
            'success': True,
            'message': 'No change needed - realtor already has this status.'
        })
        
        
# /=====================================================
@login_required
def gallery_management(request):
    """View to display all gallery images for management"""
    gallery_images = Gallery.objects.all().order_by('order', '-created_at')
    
    context = {
        'gallery_images': gallery_images,
    }
    return render(request, 'user/gallery_management.html', context)

@login_required
def add_gallery_image(request):
    """View to add a new gallery image"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if not image:
            messages.error(request, 'Please select an image to upload.')
            return redirect('gallery_management')
        
        try:
            # Create new gallery image
            gallery_image = Gallery.objects.create(
                title=title if title else None,
                description=description if description else None,
                image=image,
                order=int(order),
                is_active=is_active
            )
            
            messages.success(request, 'Gallery image added successfully!')
            
        except Exception as e:
            messages.error(request, f'Error adding gallery image: {str(e)}')
    
    return redirect('gallery_management')

@login_required
def edit_gallery_image(request):
    """View to edit an existing gallery image"""
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        
        try:
            gallery_image = get_object_or_404(Gallery, id=image_id)
            
            # Update fields
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            order = request.POST.get('order', 0)
            is_active = request.POST.get('is_active') == 'on'
            new_image = request.FILES.get('image')
            
            gallery_image.title = title if title else None
            gallery_image.description = description if description else None
            gallery_image.order = int(order)
            gallery_image.is_active = is_active
            
            # Update image if new one is provided
            if new_image:
                gallery_image.image = new_image
            
            gallery_image.save()
            
            messages.success(request, 'Gallery image updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating gallery image: {str(e)}')
    
    return redirect('gallery_management')

@login_required
def delete_gallery_image(request):
    """View to delete a gallery image"""
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        
        try:
            gallery_image = get_object_or_404(Gallery, id=image_id)
            
            # Delete the image file from storage
            if gallery_image.image:
                gallery_image.image.delete(save=False)
            
            # Delete the database record
            gallery_image.delete()
            
            messages.success(request, 'Gallery image deleted successfully!')
            
        except Exception as e:
            messages.error(request, f'Error deleting gallery image: {str(e)}')
    
    return redirect('gallery_management')


def realtor_register(request, referral_code=None):
    # Determine sponsor code
    sponsor_code = referral_code if referral_code else '44709285'  # Default sponsor code
    
    # Verify if referral code exists (optional validation)
    sponsor_exists = False
    if referral_code:
        sponsor_exists = Realtor.objects.filter(referral_code=referral_code).exists()
        if not sponsor_exists:
            sponsor_code = '44709285'  # Fall back to default if invalid
    
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            address = request.POST.get('address', '').strip()
            country = request.POST.get('country', '').strip()
            bank_name = request.POST.get('bank_name', '').strip()
            account_number = request.POST.get('account_number', '').strip()
            sponsor_code_form = request.POST.get('sponsor_code', '').strip()
            
            # Basic validation
            if not all([first_name, last_name, email, phone, address, country, bank_name, account_number]):
                messages.error(request, 'All fields are required.')
                return render(request, 'realtor_register.html', {
                    'sponsor_code': sponsor_code,
                    'form_data': request.POST
                })
            
            # Check if email already exists
            if Realtor.objects.filter(email=email).exists():
                messages.error(request, 'A realtor with this email already exists.')
                return render(request, 'realtor_register.html', {
                    'sponsor_code': sponsor_code,
                    'form_data': request.POST
                })
            
            # Handle image upload
            image = request.FILES.get('image')
            
            # Create new realtor
            realtor = Realtor(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                country=country,
                bank_name=bank_name,
                account_number=account_number,
                sponsor_code=sponsor_code_form,
                image=image
            )
            
            realtor.save()  # This will trigger the save method and generate referral_code
            
            messages.success(request, 'Registration successful! Your referral code has been generated.')
            
            # Redirect to success page or show success message with referral code
            return render(request, 'estate/realtor_register_success.html', {
                'realtor': realtor,
                'referral_code': realtor.referral_code
            })
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'estate/realtor_register.html', {
                'sponsor_code': sponsor_code,
                'form_data': request.POST
            })
    
    # GET request - show form
    return render(request, 'estate/realtor_register.html', {
        'sponsor_code': sponsor_code,
        'referral_code': referral_code
    })
    
'''nice work here'''


# views.py
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
import requests

    
 
def download_form(request, form_id):
    form = get_object_or_404(FormUpload, id=form_id)  # Replace with your model
    
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Get clean filename
        file_key = form.form_file.name
        filename = file_key.split('/')[-1]
        
        # Generate presigned URL with download headers
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_key,
                'ResponseContentDisposition': f'attachment; filename="{filename}"',
                'ResponseContentType': 'application/octet-stream'
            },
            ExpiresIn=300  # 5 minutes - short expiry for security
        )
        
        return redirect(presigned_url)
        
    except ClientError:
        raise Http404("File not found")
    except Exception:
        raise Http404("Error generating download link")