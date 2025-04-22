from django.shortcuts import render

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

