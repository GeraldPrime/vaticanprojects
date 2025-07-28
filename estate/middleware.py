from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from .models import SecretaryAdmin

class SecretaryAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is a secretary admin
        if request.user.is_authenticated:
            try:
                secretary = SecretaryAdmin.objects.get(user=request.user)
                request.is_secretary = True
                
                # Check if secretary account is active
                if not secretary.is_active:
                    messages.error(request, 'Your secretary account is inactive.')
                    return redirect('signin')
                
                # Define allowed URL patterns for secretary
                allowed_patterns = [
                    'secretary_dashboard',
                    'signout',
                    
                    # Realtor management (view and add only)
                    'realtors_page',
                    'create_realtor',
                    'realtor_detail',
                    
                    # Property Sales management (view and add only)
                    'property_sales_list',
                    'register_property_sale',
                    'property_sale_detail',
                    'property_sale_invoice',
                    
                    # Optional: If you want secretary to send client emails
                    'send_client_email',
                ]
                
                # Define allowed URL paths for secretary
                allowed_paths = [
                    '/secretary-dashboard/',
                    '/user/signout/',
                    '/signout/',
                    
                    # Realtor paths
                    '/user/realtors_page',
                    '/user/create_realtor/',
                    '/user/realtor_detail/',
                    
                    # Property Sales paths
                    '/user/property-sales/',
                    '/user/property-sales/register/',
                    '/user/property-sales/detail/',
                    '/user/property-sale/',
                    '/send-client-email/',
                ]
                
                current_path = request.path
                current_url_name = None
                
                # Try to get current URL name
                try:
                    from django.urls import resolve
                    current_url_name = resolve(current_path).url_name
                except:
                    current_url_name = None
                
                # Check if current URL is allowed
                is_allowed = (
                    current_url_name in allowed_patterns or
                    any(current_path.startswith(path) for path in allowed_paths) or
                    current_path == '/'  # Allow home page redirect
                )
                
                # Special handling for URLs with dynamic parameters
                # Allow realtor detail pages
                if '/user/realtor_detail/' in current_path:
                    is_allowed = True
                
                # Allow property sale detail and invoice pages
                if '/user/property-sales/' in current_path and current_path != '/user/property-sales/':
                    is_allowed = True
                
                if '/user/property-sale/' in current_path:
                    is_allowed = True
                
                if '/send-client-email/' in current_path:
                    is_allowed = True
                
                # Block editing URLs specifically
                blocked_edit_patterns = [
                    '/user/edit_realtor/',
                    '/user/delete-realtor/',
                    '/user/property-sale/edit/',
                    '/user/property-sales/edit/',
                ]
                
                for blocked_pattern in blocked_edit_patterns:
                    if blocked_pattern in current_path:
                        is_allowed = False
                        break
                
                # If not allowed, redirect to secretary dashboard
                if not is_allowed:
                    messages.warning(request, 'You only have access to realtor and sales management (view and add only).')
                    return redirect('secretary_dashboard')
                
            except SecretaryAdmin.DoesNotExist:
                request.is_secretary = False
        else:
            request.is_secretary = False
        
        response = self.get_response(request)
        return response