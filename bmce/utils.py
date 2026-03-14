# bmce/utils.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
import base64
import logging

logger = logging.getLogger(__name__)

def email_fetcher():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me',q='label:INBOX', maxResults=10).execute()
        messages = results.get('messages', [])
        msge = []

        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            body, attachments = parse_parts(service, msg['id'], message.get('payload', {}))

            msge.append({
                'id': msg['id'],
                'subject': headers.get('Subject', '(No Subject)'),
                'sender': headers.get('From', 'Unknown'),
                'time': headers.get('Date', ''),
                'body': body or "No content available.",
                'attachments': attachments 
            })
        return msge
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        return []

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
        elif not filename:
            # Prioritize HTML body but keep Plain Text as fallback
            if mime_type == 'text/html':
                data = part_body.get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            elif mime_type == 'text/plain' and not body:
                data = part_body.get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        elif filename:
            attachment_id = part_body.get('attachmentId')
            if attachment_id:
                try:
                    att = service.users().messages().attachments().get(
                        userId='me', messageId=msg_id, id=attachment_id
                    ).execute()
                    file_data = base64.urlsafe_b64decode(att['data'])
                    attachments.append({
                        'filename': filename,
                        'mimeType': mime_type,
                        'data': file_data 
                    })
                except Exception as e:
                    logger.error(f"Error fetching attachment {filename}: {e}")

    recurse(payload)
    return body, attachments