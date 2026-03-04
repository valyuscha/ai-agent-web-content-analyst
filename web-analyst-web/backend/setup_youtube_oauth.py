#!/usr/bin/env python3
"""Setup YouTube OAuth2 authentication"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'youtube_token.pickle'

def setup_oauth():
    """Run OAuth flow and save credentials"""
    
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ {CLIENT_SECRET_FILE} not found!")
        print("Please download OAuth2 credentials from Google Cloud Console")
        print("See YOUTUBE_OAUTH_SETUP.md for instructions")
        return False
    
    creds = None
    
    # Check if token already exists
    if os.path.exists(TOKEN_FILE):
        print(f"✓ Found existing token: {TOKEN_FILE}")
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow...")
            print("A browser window will open for authorization")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            # Use port 8090
            creds = flow.run_local_server(port=8090, 
                                         prompt='consent',
                                         authorization_prompt_message='Please visit this URL: {url}')
        
        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        print(f"✓ Credentials saved to {TOKEN_FILE}")
    
    print("\n✅ OAuth setup complete!")
    print(f"Token file: {TOKEN_FILE}")
    print("Your application can now download YouTube captions")
    return True

if __name__ == '__main__':
    setup_oauth()
