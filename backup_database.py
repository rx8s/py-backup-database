
import os
import subprocess
import datetime
import glob
import requests
import pickle
from multiprocessing import Process, Queue
from ftplib import FTP
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from upload_to_gdrive import upload_to_gdrive
from upload_to_ftp import upload_to_ftp

load_dotenv()

# Configuration from .env
BACKUP_ROOT = os.getenv("BACKUP_ROOT", "./backups")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASES = os.getenv("MYSQL_DATABASES", "").split(",")

SQLSERVER_HOST = os.getenv("SQLSERVER_HOST")
SQLSERVER_USER = os.getenv("SQLSERVER_USER")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD")
SQLSERVER_DATABASES = os.getenv("SQLSERVER_DATABASES", "").split(",")

PUSH_URL = os.getenv("PUSH_URL")

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_REMOTE_PATH = os.getenv("FTP_REMOTE_PATH", "/")

ENABLE_FTP = os.getenv("ENABLE_FTP", "true").lower() == "true"
ENABLE_GDRIVE = os.getenv("ENABLE_GDRIVE", "true").lower() == "true"

KEEP_DAYS = 7

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_PATH = 'credentials.json'
TOKEN_PATH = 'token.pickle'

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

def backup_mysql(queue):
    for db in MYSQL_DATABASES:
        db = db.strip()
        if not db:
            continue
        db_folder = os.path.join(BACKUP_ROOT, db)
        ensure_dir(db_folder)
        date_str = get_yesterday_date()
        filename = f"{date_str}.sql"
        full_path = os.path.join(db_folder, filename)
        cmd = ["mysqldump", "-u", MYSQL_USER, f"-p{MYSQL_PASSWORD}", db]
        if not is_sunday():
            cmd = [
                "mysqldump", "--single-transaction", "--quick", "--lock-tables=false",
                "-u", MYSQL_USER, f"-p{MYSQL_PASSWORD}", db
            ]
        with open(full_path, "w") as f:
            subprocess.run(cmd, stdout=f)
        cleanup_old_files(db_folder, "sql")
        queue.put(full_path)

def backup_sqlserver(queue):
    for db in SQLSERVER_DATABASES:
        db = db.strip()
        if not db:
            continue
        db_folder = os.path.join(BACKUP_ROOT, db)
        ensure_dir(db_folder)
        date_str = get_yesterday_date()
        filename = f"{date_str}.bak"
        full_path = os.path.join(db_folder, filename)
        backup_type = "DATABASE" if is_sunday() else "LOG"
        sql = f"BACKUP {backup_type} [{db}] TO DISK = N'{os.path.abspath(full_path)}' WITH INIT"
        cmd = ["sqlcmd", "-S", SQLSERVER_HOST, "-U", SQLSERVER_USER, "-P", SQLSERVER_PASSWORD, "-Q", sql]
        subprocess.run(cmd)
        cleanup_old_files(db_folder, "bak")
        queue.put(full_path)

def run_all():
    mysql_queue = Queue()
    sqlserver_queue = Queue()

    mysql_process = Process(target=backup_mysql, args=(mysql_queue,))
    sqlserver_process = Process(target=backup_sqlserver, args=(sqlserver_queue,))
    mysql_process.start()
    sqlserver_process.start()
    mysql_process.join()
    sqlserver_process.join()

    all_files = []
    while not mysql_queue.empty():
        all_files.append(mysql_queue.get())
    while not sqlserver_queue.empty():
        all_files.append(sqlserver_queue.get())

    upload_processes = []

    if ENABLE_GDRIVE:
        gdrive_proc = Process(target=upload_to_gdrive, args=(all_files,))
        gdrive_proc.start()
        upload_processes.append(gdrive_proc)

    if ENABLE_FTP:
        ftp_proc = Process(target=upload_to_ftp, args=(all_files, FTP_HOST, FTP_USER, FTP_PASSWORD, FTP_REMOTE_PATH))
        ftp_proc.start()
        upload_processes.append(ftp_proc)

    for p in upload_processes:
        p.join()

    notify()

if __name__ == "__main__":
    ensure_dir(BACKUP_ROOT)
    run_all()
