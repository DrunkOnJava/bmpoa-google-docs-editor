#!/usr/bin/env python3
"""
Google Docs API Authentication - Complete Setup Guide
Based on official Google documentation and 2024 best practices
"""

import os
import json
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes determine what access your app has
# For full read/write access to Google Docs
SCOPES = ['https://www.googleapis.com/auth/documents']

# For read-only access (more secure if you only need to read)
# SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

class GoogleDocsAuthenticator:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None
        
    def setup_instructions(self):
        """Display detailed setup instructions"""
        print("\n" + "="*70)
        print("GOOGLE DOCS API AUTHENTICATION SETUP")
        print("="*70)
        print("\nFOLLOW THESE STEPS TO SET UP AUTHENTICATION:\n")
        
        print("STEP 1: CREATE A GOOGLE CLOUD PROJECT")
        print("-" * 40)
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Click the project dropdown in the top navigation")
        print("3. Click 'New Project'")
        print("4. Enter a project name (e.g., 'BMPOA Docs Editor')")
        print("5. Click 'Create'\n")
        
        print("STEP 2: ENABLE THE GOOGLE DOCS API")
        print("-" * 40)
        print("1. In your project, go to 'APIs & Services' > 'Library'")
        print("2. Search for 'Google Docs API'")
        print("3. Click on it and press 'Enable'\n")
        
        print("STEP 3: CONFIGURE OAUTH CONSENT SCREEN")
        print("-" * 40)
        print("1. Go to 'APIs & Services' > 'OAuth consent screen'")
        print("2. Choose 'External' for user type (or 'Internal' if using Google Workspace)")
        print("3. Fill in:")
        print("   - App name: BMPOA Docs Editor")
        print("   - User support email: (your email)")
        print("   - Developer contact: (your email)")
        print("4. Click 'Save and Continue'")
        print("5. On Scopes page, click 'Add or Remove Scopes'")
        print("6. Search and add: 'https://www.googleapis.com/auth/documents'")
        print("7. Click 'Save and Continue'")
        print("8. Add your email as a test user")
        print("9. Click 'Save and Continue'\n")
        
        print("STEP 4: CREATE OAUTH 2.0 CREDENTIALS")
        print("-" * 40)
        print("1. Go to 'APIs & Services' > 'Credentials'")
        print("2. Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
        print("3. Application type: 'Desktop app'")
        print("4. Name: 'BMPOA Docs Desktop Client'")
        print("5. Click 'Create'")
        print("6. Click 'DOWNLOAD JSON' on the popup")
        print(f"7. Save the file as '{self.credentials_file}' in:")
        print(f"   {os.getcwd()}\n")
        
        print("STEP 5: RUN THIS SCRIPT AGAIN")
        print("-" * 40)
        print("After completing the above steps and saving credentials.json,")
        print("run this script again to authenticate.\n")
        print("="*70)
        
    def authenticate(self):
        """Authenticate and return credentials"""
        # Check if credentials.json exists
        if not os.path.exists(self.credentials_file):
            self.setup_instructions()
            return None
            
        # Token file stores the user's access and refresh tokens
        if os.path.exists(self.token_file):
            print("Loading saved credentials...")
            self.creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refreshing expired credentials...")
                self.creds.refresh(Request())
            else:
                print("\nStarting OAuth2 authentication flow...")
                print("A browser window will open for you to authorize access.")
                print("If the browser doesn't open automatically, copy the URL shown.\n")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                    
                # Use port 0 to let the system choose an available port
                self.creds = flow.run_local_server(
                    port=0,
                    success_message='Authentication successful! You can close this window.'
                )
                
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(self.creds.to_json())
                print(f"\n✓ Credentials saved to {self.token_file}")
                
        print("✓ Authentication successful!")
        return self.creds
        
    def build_service(self):
        """Build and return the Google Docs service"""
        if not self.creds:
            print("Error: Not authenticated. Run authenticate() first.")
            return None
            
        try:
            self.service = build('docs', 'v1', credentials=self.creds)
            return self.service
        except Exception as e:
            print(f"Error building service: {e}")
            return None
            
    def test_connection(self, document_id=None):
        """Test the API connection with a document"""
        if not self.service:
            self.build_service()
            
        if not self.service:
            return False
            
        # Use the BMPOA document ID if none provided
        if not document_id:
            document_id = "169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs"
            
        try:
            print(f"\nTesting connection with document: {document_id}")
            document = self.service.documents().get(documentId=document_id).execute()
            
            print("\n✓ SUCCESS! Connected to Google Docs API")
            print(f"Document Title: {document.get('title')}")
            print(f"Document has {len(document.get('body', {}).get('content', []))} content elements")
            
            return True
            
        except HttpError as error:
            print(f"\n✗ Error accessing document: {error}")
            
            if "insufficient authentication scopes" in str(error):
                print("\nSolution: Delete token.json and run again to re-authenticate with correct scopes")
            elif "not have permission" in str(error):
                print("\nSolution: Make sure the document is shared with your Google account")
                print("Or try with a document you own")
                
            return False
            
    def list_permissions_needed(self):
        """List the permissions this app will request"""
        print("\n" + "="*50)
        print("PERMISSIONS REQUESTED")
        print("="*50)
        print("\nThis application will request access to:")
        
        if 'https://www.googleapis.com/auth/documents' in SCOPES:
            print("✓ View and manage your Google Docs documents")
            print("  - Read document content")
            print("  - Edit document content") 
            print("  - Create new documents")
            print("  - Delete documents")
        elif 'https://www.googleapis.com/auth/documents.readonly' in SCOPES:
            print("✓ View your Google Docs documents (read-only)")
            print("  - Read document content")
            print("  - Cannot make changes")
            
        print("\nYou can revoke access at any time at:")
        print("https://myaccount.google.com/permissions")
        print("="*50)

def main():
    """Main function to run the authentication setup"""
    print("Google Docs API Authentication Tool")
    print("Version 1.0 - Based on 2024 Best Practices")
    print("="*50)
    
    # Create authenticator
    auth = GoogleDocsAuthenticator()
    
    # Show what permissions will be requested
    auth.list_permissions_needed()
    
    # Authenticate
    creds = auth.authenticate()
    
    if creds:
        # Build service
        service = auth.build_service()
        
        if service:
            # Test the connection
            print("\nWould you like to test the connection with the BMPOA document? (y/n): ", end='')
            if input().lower() == 'y':
                auth.test_connection()
            else:
                print("\nAuthentication complete! You can now use the Google Docs API.")
                print("To test with your own document, use:")
                print("  auth.test_connection('your-document-id')")
    else:
        print("\nAuthentication not completed. Please follow the setup instructions above.")
        sys.exit(1)

if __name__ == '__main__':
    main()