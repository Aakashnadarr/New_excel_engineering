# bmce/utils.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
import base64

def email_fetcher():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Added q='label:INBOX' to exclude sent mail and other labels
    results = service.users().messages().list(
        userId='me', 
        q='label:INBOX', 
        maxResults=20
    ).execute()
    
    messages = results.get('messages', [])
    msge = []

    if not messages:
        return msge

    for msg in messages:
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = message.get('payload', {}).get('headers', [])
        header_data = {h['name']: h['value'] for h in headers}
        body, attachments = parse_parts(service, msg['id'], message.get('payload', {}))

        data = {
            'subject': header_data.get('Subject', 'No Subject'),
            'sender': header_data.get('From', 'Unknown Sender'),
            'time': header_data.get('Date', 'Unknown Time'),
            'body': body,
            'attachments': attachments 
        }
        msge.append(data)

    return msge

def parse_parts(service, msg_id, payload):
    body = ""
    attachments = []

    def recurse(part):
        nonlocal body
        mime_type = part.get('mimeType', '')
        parts = part.get('parts', [])
        part_body = part.get('body', {})
        filename = part.get('filename', '')

        if parts:
            for p in parts:
                recurse(p)
        elif mime_type == 'text/plain' and not filename:
            data = part_body.get('data', '')
            if data:
                body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        elif mime_type == 'text/html' and not filename and not body:
            data = part_body.get('data', '')
            if data:
                body += base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        elif filename:
            attachment_id = part_body.get('attachmentId')
            if attachment_id:
                att = service.users().messages().attachments().get(
                    userId='me',
                    messageId=msg_id,
                    id=attachment_id
                ).execute()
                file_data = base64.urlsafe_b64decode(att['data'])
            else:
                file_data = base64.urlsafe_b64decode(part_body.get('data', ''))

            attachments.append({
                'filename': filename,
                'mimeType': mime_type,
                'data': file_data 
            })

    recurse(payload)
    return body, attachments