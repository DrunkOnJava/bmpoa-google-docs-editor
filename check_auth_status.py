#!/usr/bin/env python3
"""
Check Google Docs API Authentication Status
"""

import os
import json

def check_status():
    print("\n🔍 Google Docs API Authentication Status")
    print("="*60)
    
    # Check for credentials.json
    has_credentials = os.path.exists('credentials.json')
    has_token = os.path.exists('token.json')
    
    print(f"\n✓ credentials.json: {'FOUND' if has_credentials else 'NOT FOUND'}")
    print(f"✓ token.json: {'FOUND' if has_token else 'NOT FOUND'}")
    
    if not has_credentials:
        print("\n⚠️  NEXT STEP: Create OAuth2 credentials")
        print("\nQUICK SETUP GUIDE:")
        print("-" * 40)
        print("\n1. Open: https://console.cloud.google.com/")
        print("\n2. Create a new project (or select existing)")
        print("\n3. Enable Google Docs API:")
        print("   - Go to 'APIs & Services' > 'Library'")
        print("   - Search 'Google Docs API'")
        print("   - Click 'Enable'")
        print("\n4. Create OAuth2 credentials:")
        print("   - Go to 'APIs & Services' > 'Credentials'")
        print("   - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
        print("   - Type: 'Desktop app'")
        print("   - Name: 'BMPOA Docs Editor'")
        print("   - Download JSON")
        print(f"\n5. Save as 'credentials.json' in:\n   {os.getcwd()}")
        print("\n6. Run: python authenticate.py")
    
    elif has_credentials and not has_token:
        print("\n✓ Credentials found! Ready to authenticate.")
        print("\nNEXT STEP: Run authentication")
        print("Command: python google_docs_auth.py")
    
    elif has_credentials and has_token:
        print("\n✅ Fully authenticated!")
        
        # Try to parse token to show some info
        try:
            with open('token.json', 'r') as f:
                token_data = json.load(f)
                
            print("\nToken details:")
            if 'expiry' in token_data:
                print(f"  Expires: {token_data['expiry']}")
            if 'scopes' in token_data:
                print(f"  Scopes: {', '.join(token_data['scopes'])}")
                
        except:
            pass
            
        print("\n✓ You can now use the Google Docs API!")
        print("\nTest with: python google_docs_auth.py")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    check_status()