from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import pickle
from repository import KVStore

# Set to allow HTTP for local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"
REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"

key_value_store = KVStore()

class GoogleAuthHandler:
    def __init__(self):
        self.flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI
        )

    def get_authorization_url(self):
        """Generate Google OAuth URL for user authentication."""
        authorization_url, _ = self.flow.authorization_url(
            access_type="offline", prompt="consent", include_granted_scopes="true"
        )
        return authorization_url

    def get_credentials(self, request_url):
        """Extract credentials from Google's OAuth callback."""
        print(request_url)
        self.flow.fetch_token(authorization_response=request_url)
        user_info = self._get_user_info(self.flow.credentials)
        return user_info['email'], self.flow.credentials

    def _get_user_info(self, credentials: Credentials):
        # Initialize the OAuth2 service
        oauth2_service = build('oauth2', 'v2', credentials=credentials)
        # Retrieve user information
        user_info = oauth2_service.userinfo().get().execute()
        return user_info

    @staticmethod
    def load_credentials(email):
        """Load saved credentials from token file."""
        return pickle.loads(key_value_store.get(email))
