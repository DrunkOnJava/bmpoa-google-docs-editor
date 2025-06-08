#!/usr/bin/env python3
"""
Simple Google Docs API Authentication Script
Run this to authenticate with Google Docs API
"""

import os
import webbrowser
from google_docs_auth import GoogleDocsAuthenticator

def main():
    print("\n🔐 Google Docs API Authentication Setup")
    print("="*50)
    
    auth = GoogleDocsAuthenticator()
    
    # Check if already authenticated
    if os.path.exists('token.json'):
        print("✓ Found existing authentication token")
        print("\nOptions:")
        print("1. Test existing authentication")
        print("2. Re-authenticate (get new token)")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            creds = auth.authenticate()
            if creds:
                auth.build_service()
                auth.test_connection()
        elif choice == '2':
            os.remove('token.json')
            print("✓ Removed old token")
            creds = auth.authenticate()
            if creds:
                auth.build_service()
                auth.test_connection()
        else:
            print("Exiting...")
            return
    else:
        # First time setup
        if not os.path.exists('credentials.json'):
            print("\n⚠️  No credentials.json file found!")
            print("\nWould you like to:")
            print("1. View setup instructions")
            print("2. Open Google Cloud Console in browser")
            print("3. Exit")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                auth.setup_instructions()
                
                print("\nWould you like to open Google Cloud Console? (y/n): ", end='')
                if input().lower() == 'y':
                    webbrowser.open('https://console.cloud.google.com/')
                    
            elif choice == '2':
                print("\nOpening Google Cloud Console...")
                webbrowser.open('https://console.cloud.google.com/')
                print("\nAfter creating credentials, save them as 'credentials.json' here:")
                print(f"{os.getcwd()}")
                print("\nThen run this script again.")
            else:
                print("Exiting...")
                return
        else:
            print("✓ Found credentials.json")
            print("\nStarting authentication...")
            
            creds = auth.authenticate()
            if creds:
                auth.build_service()
                
                print("\n" + "="*50)
                print("AUTHENTICATION SUCCESSFUL!")
                print("="*50)
                
                print("\nTesting API connection...")
                auth.test_connection()
                
                print("\n✓ Setup complete! You can now use the Google Docs API.")
                print("\nNext steps:")
                print("1. Run 'python work_with_doc.py' to edit documents")
                print("2. Or use the authenticated service in your own scripts")

if __name__ == '__main__':
    main()