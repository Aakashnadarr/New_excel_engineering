from django.shortcuts import render
import os.path
from .utils import email_fetcher
import base64

def home(request):
    return render(request, 'home.html')

def email(request):
    return render(request, 'email.html')

def challan(request):
    return render(request, 'nee_challan.html')

def tax_invoice(request):
    return render(request, 'nee_tax_invoice.html')

def eway(request):
    return render(request, 'nee_eway.html')