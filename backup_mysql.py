import os
import subprocess
import datetime
import glob
import logging

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASES = os.getenv("MYSQL_DATABASES", "").split(",")
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

def backup_mysql(queue):
    for db in MYSQL_DATABASES:
        db = db.strip()
        if not db:
            continue
        try:
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

            logging.info(f"Backing up MySQL database '{db}' to {full_path}")
            result = subprocess.run(cmd, stdout=open(full_path, "w"), stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                logging.error(f"MySQL backup failed for {db}: {result.stderr}")
                continue

            cleanup_old_files(db_folder, "sql")
            queue.put(full_path)
            logging.info(f"MySQL backup completed for {db}")
        except Exception as e:
            logging.error(f"Error in MySQL backup for {db}: {e}")
