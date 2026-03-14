# bmce/consumers.py
import json
import asyncio
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import email_fetcher

class EmailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.fetching = True
        # Fetch immediately on connection
        asyncio.create_task(self.send_emails()) 
        # Start background update loop
        self.loop_task = asyncio.create_task(self.fetch_emails_loop())

    async def disconnect(self, close_code):
        self.fetching = False
        if hasattr(self, 'loop_task'):
            self.loop_task.cancel()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get('action') == 'refresh':
                await self.send_emails()
        except json.JSONDecodeError:
            pass

    async def fetch_emails_loop(self):
        while self.fetching:
            await asyncio.sleep(60)  # Extended to 60s for better performance
            if self.fetching:
                await self.send_emails()

    async def send_emails(self):
        try:
            raw_emails = await asyncio.to_thread(email_fetcher)
            processed_emails = []
            for email in raw_emails:
                attachments = []
                for att in email.get('attachments', []):
                    attachments.append({
                        'filename': att['filename'],
                        'mimeType': att['mimeType'],
                        'data_b64': base64.b64encode(att['data']).decode('utf-8')
                    })

                processed_emails.append({
                    'id': email['id'],
                    'name': email['sender'].split('<')[0].strip().replace('"', ''),
                    'from': email['sender'],
                    'subject': email['subject'],
                    'time': email['time'],
                    'body': email['body'],
                    'attachments': attachments,
                })

            await self.send(text_data=json.dumps({'emails': processed_emails}))
        except Exception as e:
            print(f"WebSocket Error: {e}")