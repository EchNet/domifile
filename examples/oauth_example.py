from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Step 1: Authenticate
SCOPES = ['https://www.googleapis.com/auth/drive.file']
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
credentials = flow.run_local_server(port=0)

# Step 2: Access Google Drive API
drive_service = build('drive', 'v3', credentials=credentials)

# Step 3: List files
results = drive_service.files().list(pageSize=10).execute()
files = results.get('files', [])
if not files:
  print('No files found.')
else:
  print('Files:')
  for file in files:
    print(f"{file['name']} ({file['id']})")

#
# User picks folder ( Javascript )
#
"""
const view = new google.picker.DocsView()
    .setIncludeFolders(true)
    .setSelectFolderEnabled(true);

const picker = new google.picker.PickerBuilder()
    .setAppId(APP_ID)
    .setOAuthToken(oauthToken)
    .addView(view)
    .setCallback(pickerCallback)
    .build();
picker.setVisible(true);
"""

#
# Handle token expiry...
#

from google.auth.transport.requests import Request

if credentials.expired and credentials.refresh_token:
  credentials.refresh(Request())

#
# Save access tokens in a database.  Fields:
# User ID (email)
# Folder ID
# Access Token
# Refresh Token
# Last Sync Date
#
