from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
from auth_handler import GoogleAuthHandler
import base64


class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, email):
        self.email = email
        self.creds = GoogleAuthHandler.load_credentials(self.email)
        self.service = build('gmail', 'v1', credentials=self.creds) 
        self.existing_labels = self.service.users().labels().list(userId='me').execute()['labels']
    
    def get_message_details(self, message_id):
        msg = self.service.users().messages().get(userId='me', id=message_id, format='full').execute()
        headers = msg['payload']['headers']
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), "Unknown Sender")
        body = None
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = part['body']['data']
                    break
        else:
            body = msg['payload']['body']['data']
    
        if body:
            body = base64.urlsafe_b64decode(body).decode('utf-8')
        else:
            body = "No plain text body found."
        return sender, subject, body

    
    def list_messages(self, query='', fetch_max_email=10):
        results = self.service.users().messages().list(
            userId='me', q=query, maxResults=fetch_max_email).execute()
        messages = results.get('messages', [])
        return messages
    
    def add_label_to_message(self, message_id, label_id):
        """Adds a label to a specific email message."""
        try:
            message = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            print(f'Label {label_id} added to message {message_id}.')
            return message
        except Exception as e:
            print(f'An error occurred: {e}')
            return None

    def send_message(self, to, subject, body):
        import base64
        from email.mime.text import MIMEText
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        
        try:
            message = self.service.users().messages().send(
                userId='me', body={'raw': raw}).execute()
            return message
        except Exception as e:
            print(f'An error occurred: {e}')
            return None


    def create_label(self, label_name):
        """Creates a new label in the user's Gmail account."""
        label = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        
        try:
            created_label = self.service.users().labels().create(
                userId='me', body=label).execute()
            return created_label
        except Exception as e:
            print(f'An error occurred: {e}')
            return None
    
    def get_label_id_from_name(self, name):
        for _ in self.existing_labels:
            if _['name'] == name:
                return _['id']

    def ensure_labels_exist(self, labels_to_ensure: list):
        """Ensures that specified labels exist in the user's Gmail account."""
        try:
            # Get the list of existing labels
            existing_labels = self.service.users().labels().list(userId='me').execute()
            existing_label_names = {label['name']: label['id'] for label in existing_labels.get('labels', [])}
            
            for label_name in labels_to_ensure:
                if label_name not in existing_label_names:
                    # Create the label if it does not exist
                    created_label = self.create_label(label_name)
                    print(f'Label "{label_name}" created with ID: {created_label["id"]}.')
                else:
                    print(f'Label "{label_name}" already exists with ID: {existing_label_names[label_name]}.')
        except Exception as e:
            print(f'An error occurred: {e}') 