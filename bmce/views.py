from django.shortcuts import render
import os.path
from .utils import email_fetcher
import base64
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import *
import openpyxl
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Worker, Attendance

def attendance(request):
    if request.method == "POST":
        worker_id = request.POST.get('worker_id')
        action = request.POST.get('action')
        worker = Worker.objects.get(id=worker_id)

        if action == "enter":
            Attendance.objects.create(worker=worker, entry_time=timezone.now())
        elif action == "exit":
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
    
    total_seconds = 0
    for log in logs:
        end_time = log.exit_time or timezone.now()
        total_seconds += (end_time - log.entry_time).total_seconds()
    
    total_seconds = int(total_seconds)
    total_hours = total_seconds // 3600
    remaining_minutes = (total_seconds % 3600) // 60
    remaining_seconds = total_seconds % 60
    
    overall_time_str = f"{total_hours}h {remaining_minutes}m {remaining_seconds}s"
    
    return render(request, 'worker_report.html', {
        'worker': worker,
        'logs': logs,
        'overall_total_time': overall_time_str
    })

def export_worker_attendance_csv(request, worker_id):
    worker = Worker.objects.get(id=worker_id)
    logs = Attendance.objects.filter(worker=worker).order_by('-entry_time')

    writer = openpyxl.Workbook()
    sheet = writer.active
    sheet.title = f"{worker.name} Attendance Report"
    sheet.append(['Entry Time', 'Exit Time', 'Duration'])
    for log in logs:
        entry_time = log.entry_time.strftime('%Y-%m-%d %H:%M:%S')
        exit_time = log.exit_time.strftime('%Y-%m-%d %H:%M:%S') if log.exit_time else 'N/A'
        duration = log.get_duration()
        sheet.append([entry_time, exit_time, duration])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{worker.name}_attendance_report.xlsx"'
    
    for column_cells in sheet.columns:
        length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = length + 2

    writer.save(response)

    return response
