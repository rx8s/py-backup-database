import os
import datetime
import logging
from multiprocessing import Process, Queue
from dotenv import load_dotenv

from upload_to_gdrive import upload_to_gdrive
from upload_to_ftp import upload_to_ftp
from notify import notify

# โหลด config
load_dotenv()

# -----------------------------
# Mode
# -----------------------------
# เลือกได้: "mysql", "mssql", หรือ "mysql,mssql"
mode = "mysql,mssql"

# -----------------------------
# Logging
# -----------------------------
LOG_FILE = "backup.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

BACKUP_ROOT = os.getenv("BACKUP_ROOT", "./backups")
PUSH_URL = os.getenv("PUSH_URL")
FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_REMOTE_PATH = os.getenv("FTP_REMOTE_PATH", "/")
ENABLE_FTP = os.getenv("ENABLE_FTP", "true").lower() == "true"
ENABLE_GDRIVE = os.getenv("ENABLE_GDRIVE", "true").lower() == "true"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def run_all(mode_str):
    start = datetime.datetime.now()

    mysql_queue = Queue()
    sqlserver_queue = Queue()
    processes = []

    selected_modes = [m.strip().lower() for m in mode_str.split(",")]

    # Import เฉพาะที่ต้องใช้
    if "mysql" in selected_modes:
        from backup_mysql import backup_mysql
        mysql_process = Process(target=backup_mysql, args=(mysql_queue,))
        processes.append(mysql_process)
        mysql_process.start()

    if "mssql" in selected_modes:
        from backup_sqlserver import backup_sqlserver
        sqlserver_process = Process(target=backup_sqlserver, args=(sqlserver_queue,))
        processes.append(sqlserver_process)
        sqlserver_process.start()

    for p in processes:
        p.join()

    all_files = []
    while not mysql_queue.empty():
        all_files.append(mysql_queue.get())
    while not sqlserver_queue.empty():
        all_files.append(sqlserver_queue.get())

    logging.info(f"Total backup files: {len(all_files)}")

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

    end = datetime.datetime.now()
    notify(
        message="Backup job completed",
        notify_url_value=PUSH_URL,
        start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=end.strftime("%Y-%m-%d %H:%M:%S"),
    )
    logging.info("Backup job completed successfully")

if __name__ == "__main__":
    ensure_dir(BACKUP_ROOT)
    run_all(mode)
