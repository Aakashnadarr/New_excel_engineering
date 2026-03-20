from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('email/', email, name='email'),
    path('challan/', challan, name='challan'),  
    path('bill/', tax_invoice, name='tax_invoice'),
    path('attendance/', attendance, name='attendance'),
    path('attendance/report/<int:worker_id>/', worker_report, name='worker_report'),
]