# 🛡️ Multi-Process Database Backup System

โปรแกรม Python สำหรับ Backup ฐานข้อมูล **MySQL** และ **SQL Server** แบบแยกกระบวนการทำงาน (Multi-Process) รองรับการทำงานทั้งบน Windows, Linux และ macOS พร้อมระบบจัดการไฟล์ย้อนหลัง, แจ้งเตือน และอัปโหลดขึ้น Google Drive อัตโนมัติ

---

## 📌 คุณสมบัติ

- ✅ Backup ฐานข้อมูล **MySQL** และ **SQL Server**
- ✅ ทำงานแบบ **Multi-PID** แยกกระบวนการระหว่าง MySQL และ SQL Server
- ✅ รองรับระบบปฏิบัติการ **Windows / Linux / macOS**
- ✅ ตั้งเวลารันทุกวันเวลา **01:00**
- ✅ Backup แบบ:
  - **Full Backup** ในวันอาทิตย์
  - **Daily Backup** (เฉพาะข้อมูลเปลี่ยนแปลง) ในวันอื่นๆ
- ✅ สร้างโฟลเดอร์แยกตามชื่อฐานข้อมูล
- ✅ ตั้งชื่อไฟล์เป็นวันที่ของ "เมื่อวาน" (เช่น `2025-07-24.sql`)
- ✅ ลบไฟล์ backup ที่เก่ากว่า **7 วัน**
- ✅ ส่ง **Push Notification** ไปยัง URL หลัง Backup เสร็จ
- ✅ **อัปโหลดไฟล์ขึ้น Google Drive** อัตโนมัติ

---

## 📂 โครงสร้างโฟลเดอร์ที่สร้าง

backups/
├── db1/
│ ├── 2025-07-24.sql
│ └── ...
├── db3/
│ ├── 2025-07-24.bak
│ └── ...

---

## ⚙️ การติดตั้ง

### 1. ติดตั้ง Python Packages
```bash
pip install requests google-api-python-client google-auth-httplib2 google-auth-oauthlib
2. เปิดใช้งาน Google Drive API
ไปที่ Google Cloud Console

สร้าง Project → เปิดใช้ Google Drive API

ไปที่เมนู Credentials → สร้าง OAuth 2.0 Client ID แบบ "Desktop"

ดาวน์โหลด credentials.json → วางไว้ในโฟลเดอร์เดียวกับ script

3. รัน Script ครั้งแรก
bash

python backup_multiprocess.py
ระบบจะเปิดเบราว์เซอร์ให้ login เพื่อยืนยันสิทธิ์ Google Drive และสร้างไฟล์ token.pickle

🕐 ตั้งเวลาทำงานอัตโนมัติ
Linux/macOS (crontab)
bash

crontab -e
เพิ่ม:

swift

0 1 * * * /usr/bin/python3 /full/path/to/backup_multiprocess.py
Windows (Task Scheduler)
Trigger: 01:00 ทุกวัน

Action:

Program: python

Arguments: C:\path\to\backup_multiprocess.py

🛠️ การตั้งค่า (ภายในโค้ด)
แก้ไขตัวแปรใน backup_multiprocess.py ตามต้องการ:

python

BACKUP_ROOT = "/your/backup/folder"
MYSQL_USER = "root"
MYSQL_PASSWORD = "yourpassword"
MYSQL_DATABASES = ["db1", "db2"]
SQLSERVER_HOST = "localhost"
SQLSERVER_USER = "sa"
SQLSERVER_PASSWORD = "yourpassword"
SQLSERVER_DATABASES = ["db3", "db4"]
PUSH_URL = "https://example.com/push-msg"
📤 การ Backup SQL Server แบบ Incremental
ใช้ BACKUP LOG สำหรับ Daily Backup

หรือเปลี่ยนเป็น DIFFERENTIAL ได้ (กรณีตั้งค่าระบบให้รองรับ)

✅ License
MIT License

🙋 Support
หากคุณต้องการปรับแต่งเพิ่มเติม เช่น:

ตั้งค่าผ่าน .env

แสดง log ลงไฟล์ .log

ส่งแจ้งเตือนผ่าน LINE Notify

สามารถขอคำแนะนำเพิ่มเติมได้ทุกเมื่อ