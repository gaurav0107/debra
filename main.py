from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

from auth_handler import GoogleAuthHandler
from gmail_manager import GmailService
from calendar_manager import CalendarService

app = FastAPI()
auth_handler = GoogleAuthHandler()


@app.get("/")
def home():
    return {"message": "Welcome to OAuth API"}


@app.get("/authorize")
def authorize():
    """Redirect user to Google's OAuth login."""
    auth_url = auth_handler.get_authorization_url()
    print(auth_url)
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
def auth_callback(request: Request):
    """Handle OAuth callback and extract tokens."""
    tokens = auth_handler.get_credentials(str(request.url))
    return JSONResponse(content={"message": "Authentication successful", **tokens})


@app.get("/gmail/messages")
def get_gmail_messages():
    """Fetch unread Gmail messages."""
    gmail_service = GmailService()
    messages = gmail_service.list_messages()
    return JSONResponse(content={"messages": messages})


@app.get("/calendar/events")
def get_calendar_events():
    """Fetch upcoming Google Calendar events."""
    calendar_service = CalendarService()
    events = calendar_service.list_events()
    return JSONResponse(content={"events": events})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
