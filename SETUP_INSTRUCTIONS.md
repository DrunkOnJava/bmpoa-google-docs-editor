# Setting Up Service Account for BMPOA Document Editing

## Steps to Create Service Account Key:

1. **You're already on the correct page!** You're viewing the `google-docs-tool@healthportal-445118.iam.gserviceaccount.com` service account.

2. **Click on the "KEYS" tab** at the top of the page (next to "DETAILS", "PERMISSIONS", etc.)

3. **Click "ADD KEY"** button → Select **"Create new key"**

4. **Choose "JSON"** as the key type

5. **Click "CREATE"** - This will download a JSON key file to your computer

6. **Save the file** as `service-account-key.json` in your project directory:
   ```
   /Users/griffin/Projects/bmpoa-google-docs-editor/service-account-key.json
   ```

## After downloading the key:

1. **Share the BMPOA document** with the service account:
   - Open: https://docs.google.com/document/d/169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs
   - Click "Share"
   - Add email: `google-docs-tool@healthportal-445118.iam.gserviceaccount.com`
   - Give "Editor" permissions
   - Click "Send"

2. **Run the script**:
   ```bash
   cd /Users/griffin/Projects/bmpoa-google-docs-editor
   ./gdocs_env/bin/python use_service_account.py
   ```

## Security Note:
- Keep the JSON key file secure and never commit it to version control
- Add `*.json` to your `.gitignore` file to prevent accidental commits

The service account method is more reliable than OAuth for automated scripts and doesn't require browser authentication!