
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os
from ftplib import FTP

from dotenv import load_dotenv
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_PATH = 'credentials.json'
TOKEN_PATH = 'token.pickle'

def upload_to_gdrive(files):
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    service = build('drive', 'v3', credentials=creds)
    for file_path in files:
        try:
            file_metadata = {'name': os.path.basename(file_path)}
            media = MediaFileUpload(file_path, resumable=True)
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"[Google Drive] Uploaded: {file_path}")
        except Exception as e:
            print(f"[Google Drive] Upload failed: {file_path} | {e}")
