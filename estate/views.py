from django.shortcuts import render,redirect, get_object_or_404


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

from django.contrib.auth.forms import PasswordChangeForm                                   # :contentReference[oaicite:0]{index=0}
from django.contrib.auth import update_session_auth_hash   



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


# ====================================ADMIN INTERFACE===========================================
@login_required
def userhome(request):
    return render(request, "user/home.html")

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
    

def signout(request):
    logout(request)
    messages.success(request, "logout successful")
    return redirect('signin')