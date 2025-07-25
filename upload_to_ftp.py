
import os
from ftplib import FTP

def upload_to_ftp(files, host, user, password, remote_path):
    try:
        ftp = FTP(host)
        ftp.login(user, password)
        if remote_path:
            parts = remote_path.strip('/').split('/')
            for part in parts:
                if part not in ftp.nlst():
                    ftp.mkd(part)
                ftp.cwd(part)
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    ftp.storbinary(f'STOR {os.path.basename(file_path)}', f)
                print(f"[FTP] Uploaded: {file_path}")
            except Exception as e:
                print(f"[FTP] Upload failed: {file_path} | {e}")
        ftp.quit()
    except Exception as e:
        print(f"[FTP] Connection failed: {e}")
