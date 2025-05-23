from django.urls import path
from . import views


from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('buildingprojects/', views.buildingprojects, name='buildingprojects'),
    path('estates/', views.estates, name='estates'),
    path('downloadables/', views.downloadables, name='downloadables'),
    path('contact/', views.contact, name='contact'),
    path('realtors-check/', views.realtors_check, name='realtors_check'),
    
    
    # ======================ADMIN URLS=================================
    
    path('user/', views.userhome, name='user'),
    path('user/signin/', views.signin, name='signin'),

    path('user/signout/', views.signout, name='signout'),
    path('user/profile/', views.profile, name='profile'),
    path('user/create_realtor/', views.create_realtor, name='create_realtor'),
    path('user/realtor_detail/<int:id>', views.realtor_detail, name='realtor_detail'),
    path('user/edit_realtor/<int:id>', views.edit_realtor, name='edit_realtor'),
    path('user/realtors_page', views.realtors_page, name='realtors_page'),
    path('user/delete-realtor/<int:id>/', views.delete_realtor, name='delete_realtor'),
    
    
    # Password reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
     
    
    
    path('user/pay-all-commissions/<int:realtor_id>/', views.pay_all_commissions, name='pay_all_commissions'),
    path('pay-commission/<int:commission_id>/', views.pay_commission, name='pay_commission'),
    
    
    # Property URLs
    path('user/properties/', views.property_list, name='property_list'),
    path('user/properties/register/', views.register_property, name='register_property'),
    path('user/properties/<int:property_id>/', views.property_detail, name='property_detail'),
    path('user/property/edit/<int:property_id>/', views.edit_property, name='edit_property'),
    path('user/property/<int:property_id>/delete/', views.delete_property, name='delete_property'),
    
    # commission URLs
    path('user/commissions/', views.commissions_list, name='commissions_list'),
    
    # Property Sales URLs
    path('user/property-sales/', views.property_sales_list, name='property_sales_list'),
    path('user/property-sales/register/', views.register_property_sale, name='register_property_sale'),
    path('user/property-sales/<int:id>/', views.property_sale_detail, name='property_sale_detail'),
    path('user/property-sale/<int:sale_id>/invoice/', views.property_sale_invoice, name='property_sale_invoice'),
    
    
    # Frontend Extras URLs
    path('user/frontend-extras/', views.frontend_extras, name='frontend_extras'),
    path('user/frontend-extras/forms/upload/', views.upload_form, name='upload_form'),
    path('user/frontend-extras/forms/', views.forms_list, name='forms_list'),
    path('user/frontend-extras/forms/<int:form_id>/edit/', views.edit_form, name='edit_form'),
    path('user/frontend-extras/forms/<int:form_id>/delete/', views.delete_form, name='delete_form'),
    
    # general settings: 
    path('user/settings/general/', views.general_settings, name='general_settings'),
    
    
    
]
if settings.DEBUG:  # Only serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
