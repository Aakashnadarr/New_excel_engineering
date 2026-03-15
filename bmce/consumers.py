# bmce/consumers.py
import json
import asyncio
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
# Import your upgraded fetcher and the parser
from .utils import email_fetcher, parse_parts, build_gmail_service

class EmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.fetching = True
        # Initial fast sync of 500 snippets
        asyncio.create_task(self.sync_inbox()) 
        # Background update loop
        self.loop_task = asyncio.create_task(self.fetch_emails_loop())

    async def disconnect(self, close_code):
        self.fetching = False
        if hasattr(self, 'loop_task'):
            self.loop_task.cancel()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh':
                await self.sync_inbox()
            
            # NEW: Action to load full body/attachments only when a user clicks an email
            elif action == 'get_details':
                email_id = data.get('email_id')
                if email_id:
                    await self.send_email_details(email_id)
        except json.JSONDecodeError:
            pass

    async def fetch_emails_loop(self):
        while self.fetching:
            await asyncio.sleep(120) # Check for new mail every 2 mins
            if self.fetching:
                await self.sync_inbox()

    async def sync_inbox(self):
        """Syncs the sidebar list for 500 emails using snippets."""
        try:
            # Calls the batching fetcher (max_results=500)
            raw_emails = await asyncio.to_thread(email_fetcher, 500)
            
            processed_list = []
            for email in raw_emails:
                processed_list.append({
                    'id': email['id'],
                    'name': email['sender'].split('<')[0].strip().replace('"', ''),
                    'from': email['sender'],
                    'subject': email['subject'],
                    'time': email['time'],
                    'snippet': email['snippet'], # Lightweight text for the sidebar
                })

            # Send the metadata list to populate the UI instantly
            await self.send(text_data=json.dumps({
                'type': 'list',
                'emails': processed_list
            }))
        except Exception as e:
            print(f"Sync Error: {e}")

    async def send_email_details(self, email_id):
        """Fetches and sends the full body and attachments for ONE specific email."""
        try:
            # We fetch the full details specifically for this ID
            # Use a helper to get the service and message
            service = await asyncio.to_thread(build_gmail_service)
            message = await asyncio.to_thread(
                lambda: service.users().messages().get(userId='me', id=email_id, format='full').execute()
            )
            
            # Parse full content only for this one email
            body, raw_attachments = await asyncio.to_thread(
                parse_parts, service, email_id, message.get('payload', {})
            )

            processed_attachments = []
            for att in raw_attachments:
                processed_attachments.append({
                    'filename': att['filename'],
                    'mimeType': att['mimeType'],
                    'data_b64': base64.b64encode(att['data']).decode('utf-8')
                })

            # Send only the details for the selected email
            await self.send(text_data=json.dumps({
                'type': 'details',
                'email_id': email_id,
                'body': body,
                'attachments': processed_attachments
            }))
        except Exception as e:
            print(f"Error loading email details: {e}")