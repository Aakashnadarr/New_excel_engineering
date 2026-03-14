from django.shortcuts import render
import os.path
from .utils import email_fetcher
import base64



def index(request):
    return render(request, 'email.html')

def detail_inbox(request, email_id):
    # Placeholder for email detail view
    return render(request, 'email_detail.html', {'email_id': email_id})