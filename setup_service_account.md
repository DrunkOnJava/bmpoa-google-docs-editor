# Alternative: Service Account Setup for Google Docs API

Since browser-based OAuth2 requires interactive authentication, you can use a service account instead for programmatic access.

## Steps to Create a Service Account:

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com/
   - Select your project (bmpoa-docs-editor)

2. **Create Service Account**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "+ CREATE SERVICE ACCOUNT"
   - Name: "bmpoa-docs-service"
   - Description: "Service account for BMPOA Docs API access"
   - Click "Create and Continue"
   - Skip the optional steps, click "Done"

3. **Create Key**
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON"
   - Save the file as `service-account-key.json` in this directory

4. **Share Document with Service Account**
   - Copy the service account email (ends with @...iam.gserviceaccount.com)
   - Open your Google Doc
   - Click "Share"
   - Paste the service account email
   - Give it "Editor" access

## Alternative: Run OAuth2 Locally

If you prefer OAuth2 (more secure for personal use):

1. **On your local machine**, run:
   ```bash
   cd /Users/griffin/Projects/bmpoa-google-docs-editor
   source gdocs_env/bin/activate
   python google_docs_auth.py
   ```

2. A browser will open for authentication

3. After authenticating, a `token.json` file will be created

4. You can then use the authenticated session

## Which method do you prefer?
- **Service Account**: Better for automation, no browser needed
- **OAuth2**: Better for personal use, requires browser authentication once