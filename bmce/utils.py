# bmce/utils.py
import os.path
import base64
import logging
import time
import random
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

logger = logging.getLogger(__name__)

def build_gmail_service():
    """Helper function to authenticate and return the Gmail API service."""
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

    return build('gmail', 'v1', credentials=creds)

def email_fetcher(max_results=500):
    """Fetches list of emails using batch requests and backoff to avoid 429 errors."""
    try:
        service = build_gmail_service()
        
        # Primary inbox query with exclusions
        results = service.users().messages().list(
            userId='me', 
            q='label:INBOX category:primary -from:HDFC -from:SBI', 
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            return []

        msge = []
        failed_ids = []

        def callback(request_id, response, exception):
            if exception is not None:
                # If rate limited (429), track the ID for retry
                if isinstance(exception, HttpError) and exception.resp.status == 429:
                    failed_ids.append(request_id)
                else:
                    logger.error(f"Error fetching {request_id}: {exception}")
            else:
                headers = {h['name']: h['value'] for h in response.get('payload', {}).get('headers', [])}
                msge.append({
                    'id': response['id'],
                    'internalDate': int(response.get('internalDate', 0)),
                    'subject': headers.get('Subject', '(No Subject)'),
                    'sender': headers.get('From', 'Unknown'),
                    'time': headers.get('Date', ''),
                    'snippet': response.get('snippet', ''),
                    'payload': response.get('payload', {})
                })

        def run_batch(msg_list):
            batch = service.new_batch_http_request(callback=callback)
            for m in msg_list:
                batch.add(service.users().messages().get(userId='me', id=m['id'], format='full'), request_id=m['id'])
            batch.execute()

        # Process in smaller chunks (50) to avoid overwhelming the API
        chunk_size = 50
        for i in range(0, len(messages), chunk_size):
            current_chunk = messages[i:i + chunk_size]
            
            retries = 0
            while retries < 5:
                run_batch(current_chunk)
                
                if not failed_ids:
                    break
                
                # Exponential backoff: 2^retries + random jitter
                wait_time = (2 ** retries) + random.random()
                logger.warning(f"Rate limited. Waiting {wait_time:.2f}s before retry...")
                time.sleep(wait_time)
                
                # Setup next retry for failed messages only
                current_chunk = [{'id': fid} for fid in failed_ids]
                failed_ids = []
                retries += 1

        # Final Sort: Newest First
        return sorted(msge, key=lambda x: x['internalDate'], reverse=True)

    except Exception as e:
        logger.error(f"Critical error in email_fetcher: {e}")
        return []

def parse_parts(service, msg_id, payload):
    """Parses email parts to extract body text and attachments."""
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

def scrape_gst_details(gst_number: str) -> dict:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    with webdriver.Chrome(options=options) as driver:
        url = "https://cleartax.in/gst-number-search/"
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 15)
            input_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, r"input[placeholder*='Enter company name or GSTIN']")))
            input_field.send_keys(gst_number)
            search_btn = driver.find_element(By.CSS_SELECTOR, r"#__next > div > div.wg-container.relative > div.mt-20.w-3\/4.sm\:w-full.sm\:mt-12 > div:nth-child(3) > div:nth-child(2) > div > button")
            search_btn.click()
            details_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, r"#__next > div > div.wg-container.relative > div.mt-20.w-3\/4.sm\:w-full.sm\:mt-12 > div:nth-child(3) > div.my-10.relative > div.bg-white.w-full.z-10 > div > div")))
        
            lines = [line.strip() for line in details_container.text.split("\n") if line.strip()]
            data = dict(zip(lines[0::2], lines[1::2]))
            data["scraped_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            return data

        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}"}