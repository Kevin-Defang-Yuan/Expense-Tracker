from django.shortcuts import render
from django.http import HttpResponse

# Tutorial Mode
# Create your views here.
def dashboard(request):
    return HttpResponse('Hello World')