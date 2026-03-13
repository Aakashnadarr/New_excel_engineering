from django.shortcuts import render
import os.path
from .utils import email_fetcher
import base64



def index(request):
    
    
    emails = []
    for i, email in enumerate(email_fetcher()):
        attachments = []
        for att in email.get('attachments', []):
            attachments.append({
                'filename': att['filename'],
                'mimeType': att['mimeType'],
                'data_b64': base64.b64encode(att['data']).decode('utf-8')
            })

        emails.append({
                'id': i + 1,
                'name': email['sender'].split('<')[0].strip(),
                'from': email['sender'],
                'subject': email['subject'],
                'time': email['time'],
                'body': email.get('body', 'No content'),  # ← make sure this exists
                'attachments': attachments,
            })
    
    return render(request, 'email.html', {'emails': emails})

def detail_inbox(request, email_id):
    # Placeholder for email detail view
    return render(request, 'email_detail.html', {'email_id': email_id})