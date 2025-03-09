from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import pickle

# Set to allow HTTP for local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

CLIENT_SECRETS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"
REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"


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
        self.flow.fetch_token(authorization_response=request_url)
        credentials = self.flow.credentials

        # Store tokens securely (use DB in production)
        token_data = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        }

        with open(TOKEN_FILE, "wb") as token_file:
            pickle.dump(credentials, token_file)

        return token_data

    @staticmethod
    def load_credentials():
        """Load saved credentials from token file."""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token_file:
                return pickle.load(token_file)
        return None
