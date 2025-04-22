from django.urls import path
from . import views

urlpatterns = [
    path('/', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('buildingprojects/', views.buildingprojects, name='buildingprojects'),
    path('estates/', views.estates, name='estates'),
    path('downloadables/', views.downloadables, name='downloadables'),
    path('contact/', views.contact, name='contact'),
]