import os
import subprocess
import datetime
import glob
import logging

SQLSERVER_HOST = os.getenv("SQLSERVER_HOST")
SQLSERVER_USER = os.getenv("SQLSERVER_USER")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD")
SQLSERVER_DATABASES = os.getenv("SQLSERVER_DATABASES", "").split(",")
BACKUP_ROOT = os.getenv("BACKUP_ROOT", "./backups")
KEEP_DAYS = int(os.getenv("KEEP_DAYS", 7))

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
            try:
                os.remove(f)
                logging.info(f"Deleted old file: {f}")
            except Exception as e:
                logging.error(f"Error deleting file {f}: {e}")

def backup_sqlserver(queue):
    for db in SQLSERVER_DATABASES:
        db = db.strip()
        if not db:
            continue
        try:
            db_folder = os.path.join(BACKUP_ROOT, db)
            ensure_dir(db_folder)
            date_str = get_yesterday_date()
            filename = f"{date_str}.bak"
            full_path = os.path.join(db_folder, filename)

            backup_type = "DATABASE" if is_sunday() else "LOG"
            sql = f"BACKUP {backup_type} [{db}] TO DISK = N'{os.path.abspath(full_path)}' WITH INIT"

            logging.info(f"Backing up SQL Server database '{db}' ({backup_type}) to {full_path}")
            result = subprocess.run(
                ["sqlcmd", "-S", SQLSERVER_HOST, "-U", SQLSERVER_USER, "-P", SQLSERVER_PASSWORD, "-Q", sql],
                stderr=subprocess.PIPE, text=True
            )

            if result.returncode != 0:
                logging.error(f"SQL Server backup failed for {db}: {result.stderr}")
                continue

            cleanup_old_files(db_folder, "bak")
            queue.put(full_path)
            logging.info(f"SQL Server backup completed for {db}")
        except Exception as e:
            logging.error(f"Error in SQL Server backup for {db}: {e}")
