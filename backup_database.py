import os
import subprocess
import datetime
import glob
import platform
import requests
import pickle
from multiprocessing import Process
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# === CONFIG ===
BACKUP_ROOT = "/your/backup/folder"  # Absolute path เช่น "/home/user/backups" หรือ "C:/backups"
MYSQL_USER = "root"
MYSQL_PASSWORD = "yourpassword"
MYSQL_DATABASES = ["db1", "db2"]

SQLSERVER_HOST = "localhost"
SQLSERVER_USER = "sa"
SQLSERVER_PASSWORD = "yourpassword"
SQLSERVER_DATABASES = ["db3", "db4"]

PUSH_URL = "https://example.com/push-msg"
KEEP_DAYS = 7

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_PATH = 'credentials.json'
TOKEN_PATH = 'token.pickle'

# === UTILITY ===

def get_yesterday_date():
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

def is_sunday():
    return datetime.datetime.now().weekday() == 6

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def cleanup_old_files(folder, ext):
    files = sorted(glob.glob(os.path.join(folder, f"*.{ext}")))
    if len(files) > KEEP_DAYS:
        for f in files[:-KEEP_DAYS]:
            os.remove(f)

def notify():
    try:
        requests.get(PUSH_URL)
    except Exception as e:
        print(f"Push notify failed: {e}")

def upload_to_gdrive(file_path):
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
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# === BACKUP PROCESS: MYSQL ===

def backup_mysql():
    for db in MYSQL_DATABASES:
        db_folder = os.path.join(BACKUP_ROOT, db)
        ensure_dir(db_folder)
        date_str = get_yesterday_date()
        filename = f"{date_str}.sql"
        full_path = os.path.join(db_folder, filename)

        cmd = [
            "mysqldump",
            "--single-transaction",
            "--quick",
            "--lock-tables=false",
            "-u", MYSQL_USER,
            f"-p{MYSQL_PASSWORD}",
            db
        ]
        if is_sunday():
            cmd = ["mysqldump", "-u", MYSQL_USER, f"-p{MYSQL_PASSWORD}", db]

        with open(full_path, "w") as f:
            subprocess.run(cmd, stdout=f)

        cleanup_old_files(db_folder, "sql")
        upload_to_gdrive(full_path)

# === BACKUP PROCESS: SQL SERVER ===

def backup_sqlserver():
    for db in SQLSERVER_DATABASES:
        db_folder = os.path.join(BACKUP_ROOT, db)
        ensure_dir(db_folder)
        date_str = get_yesterday_date()
        filename = f"{date_str}.bak"
        full_path = os.path.join(db_folder, filename)

        if is_sunday():
            backup_type = "DATABASE"
        else:
            backup_type = "LOG"  # ต้องตั้ง recovery mode เป็น FULL

        sql = f"BACKUP {backup_type} [{db}] TO DISK = N'{os.path.abspath(full_path)}' WITH INIT"
        cmd = [
            "sqlcmd",
            "-S", SQLSERVER_HOST,
            "-U", SQLSERVER_USER,
            "-P", SQLSERVER_PASSWORD,
            "-Q", sql
        ]
        subprocess.run(cmd)

        cleanup_old_files(db_folder, "bak")
        upload_to_gdrive(full_path)

# === MAIN ENTRY ===

def run_all():
    mysql_process = Process(target=backup_mysql)
    sqlserver_process = Process(target=backup_sqlserver)

    mysql_process.start()
    sqlserver_process.start()

    mysql_process.join()
    sqlserver_process.join()

    notify()

if __name__ == "__main__":
    ensure_dir(BACKUP_ROOT)
    run_all()
