from django.shortcuts import render
import os.path
from .utils import email_fetcher
import base64

def home(request):
    return render(request, 'home.html')

def email(request):
    return render(request, 'email.html')
