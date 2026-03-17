from django.urls import include, path

from .views import *

urlpatterns = [
    path('',home, name='home'),
    path('email/', email, name='email'),
    path('challan/', challan, name='challan'),  
    path('bill/', tax_invoice, name='tax_invoice'),
    path('eway/', eway, name='eway'),
]
