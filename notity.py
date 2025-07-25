import os
import requests
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime, time

from dotenv import load_dotenv

load_dotenv()

# Config ผ่าน env หรือ parameter (แก้ไขให้เหมาะสมกับโปรเจกต์คุณ)
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_TO_USER_ID = os.getenv("LINE_TO_USER_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

# กำหนดเวลาที่อนุญาตให้แจ้งเตือน เช่น "08:00" ถึง "20:00"
NOTIFY_START_TIME = os.getenv("NOTIFY_START_TIME", "00:00")
NOTIFY_END_TIME = os.getenv("NOTIFY_END_TIME", "23:59")

def _is_within_notify_time():
    now = datetime.now().time()
    start = time.fromisoformat(NOTIFY_START_TIME)
    end = time.fromisoformat(NOTIFY_END_TIME)
    if start <= end:
        return start <= now <= end
    else:
        # กรณีข้ามคืน เช่น 22:00 - 06:00
        return now >= start or now <= end

def notify_line(message):
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("[Notify] LINE token missing")
        return
    try:

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN
        }
        payload = {
            "to": LINE_TO_USER_ID,
            "messages":[
                {
                    "type": "text",
                    "text": message
                }
            ]
        }
        print(headers)
        print(payload)
        response = requests.post("https://api.line.me/v2/bot/message/push", data=json.dumps(payload), headers=headers)
        print(response)
        print("ส่งข้อความสำเร็จ")
        
    except Exception as e:
        print(f"[Notify][ERR] LINE notify exception: {e}")

def notify_discord(message):
    if not DISCORD_WEBHOOK_URL:
        print("[Notify] Discord webhook missing")
        return
    data = {"content": message}
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if resp.status_code == 204:
            print("[Notify] Discord notification sent")
        else:
            print(f"[Notify] Discord notify failed: {resp.text}")
    except Exception as e:
        print(f"[Notify] Discord notify exception: {e}")

def notify_email(subject, message):
    if not (EMAIL_SMTP_SERVER and EMAIL_USER and EMAIL_PASSWORD and EMAIL_TO):
        print("[Notify] Email config missing")
        return
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg.set_content(message)

        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("[Notify] Email notification sent")
    except Exception as e:
        print(f"[Notify] Email notify exception: {e}")

def notify_url(url):
    if not url:
        print("[Notify] Notify URL missing")
        return
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            print("[Notify] URL notification sent")
        else:
            print(f"[Notify] URL notify failed: {resp.text}")
    except Exception as e:
        print(f"[Notify] URL notify exception: {e}")

def notify(message, subject="Backup Notification", notify_url_value=None, start_time=None, end_time=None):
    """
    message: ข้อความแจ้งเตือนหลัก
    subject: หัวข้อ email (ถ้าใช้ email)
    notify_url_value: URL สำหรับแจ้งผ่าน HTTP GET
    start_time: datetime object หรือ string แสดงเวลาที่เริ่ม backup
    end_time: datetime object หรือ string แสดงเวลาที่จบ backup
    """
    if start_time and end_time:
        time_info = f"Backup started at: {start_time}\nBackup finished at: {end_time}\n"
        message = time_info + message

    if not _is_within_notify_time():
        print("[Notify] Current time outside notification window. Skipping notify.")
        return

    if LINE_CHANNEL_ACCESS_TOKEN:
        print('this')
        notify_line(message)
        print('this')
    if DISCORD_WEBHOOK_URL:
       notify_discord(message)
    if EMAIL_SMTP_SERVER:
       notify_email(subject, message)
    # if notify_url_value:
    #    notify_url(notify_url_value)


notify(
        message="Backup job completed successfully",
        start_time= datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )