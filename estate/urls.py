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
    
    
    # ======================ADMIN URLS=================================
    
    path('user/', views.userhome, name='user'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
]
if settings.DEBUG:  # Only serve media files during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
