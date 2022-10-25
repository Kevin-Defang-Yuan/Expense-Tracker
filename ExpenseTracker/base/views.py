from django.shortcuts import render
from django.http import HttpResponse

# Tutorial Mode
# Create your views here.
def index(request):
    return HttpResponse('Hello World')