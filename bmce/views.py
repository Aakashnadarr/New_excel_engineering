from django.shortcuts import render
import os.path
from .utils import email_fetcher
import base64
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import *

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Worker, Attendance

def attendance(request):
    if request.method == "POST":
        worker_id = request.POST.get('worker_id')
        action = request.POST.get('action')
        worker = Worker.objects.get(id=worker_id)

        if action == "enter":
            # Create a new attendance record for entry
            Attendance.objects.create(worker=worker, entry_time=timezone.now())
        elif action == "exit":
            # Find the active session and set the exit time
            latest_record = Attendance.objects.filter(worker=worker, exit_time__isnull=True).last()
            if latest_record:
                latest_record.exit_time = timezone.now()
                latest_record.save()
        
        return redirect('attendance')

    # Prepare data for the template
    workers = Worker.objects.all()
    for worker in workers:
        active_session = Attendance.objects.filter(worker=worker, exit_time__isnull=True).last()
        worker.is_present = bool(active_session)
        worker.current_session = active_session

    return render(request, 'attendance.html', {'workers': workers})
def home(request):
    return render(request, 'home.html')

def email(request):
    return render(request, 'email.html')

def challan(request):
    return render(request, 'nee_challan.html')

def tax_invoice(request):
    return render(request, 'nee_tax_invoice.html')

def worker_report(request, worker_id):
    worker = Worker.objects.get(id=worker_id)
    logs = Attendance.objects.filter(worker=worker).order_by('-entry_time')
    
    # Calculate the total hours across all finished sessions
    total_cumulative_time = sum(log.get_duration() for log in logs)
    
    context = {
        'worker': worker,
        'logs': logs,
        'total_cumulative_time': round(total_cumulative_time, 2)
    }
    return render(request, 'worker_report.html', context)

