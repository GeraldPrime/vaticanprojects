from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(UserAdmin):
   
    list_display = ('username','first_name','last_name', 'email','is_staff','last_login', "image" )
    search_fields = ('username', 'email', )
    readonly_fields = ('date_joined', 'last_login')
    
    # model = User
    # fieldsets = BaseUserAdmin.fieldsets + (
    #     (None, {'fields': ('image',)}),
    # )
    

admin.site.register(User, CustomUserAdmin)
    
   
    
