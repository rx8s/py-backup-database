# 🛡️ Multi-Process Database Backup System

ระบบสำรองข้อมูลฐานข้อมูล MySQL และ SQL Server แบบ Multi-Process (แยก PID) ที่ทำงานอัตโนมัติทุกวันเวลา 01:00 น. พร้อมอัปโหลดไฟล์ขึ้น Google Drive และแจ้งเตือนผ่าน URL ที่กำหนด

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.7%2B-green)
![MySQL](https://img.shields.io/badge/Database-MariaDB%20%7C%20MySQL%20%7C%20SQL_Server-yellow)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

---

## 🚀 ฟีเจอร์

- ✅ รองรับ MySQL และ SQL Server
- ✅ แยก Process สำหรับการ Backup ของแต่ละระบบ (Multi-PID)
- ✅ ทำงานได้บนทุกระบบปฏิบัติการ: **Windows / Linux / macOS**
- ✅ สำรองข้อมูลอัตโนมัติทุกวันเวลา 01:00 น.
  - **วันอาทิตย์** → Full Backup
  - **วันอื่นๆ** → Daily (เฉพาะข้อมูลเปลี่ยนแปลง)
- ✅ ตั้งชื่อไฟล์ตามวันที่ของเมื่อวาน (เช่น `2025-07-24.sql`)
- ✅ แยกโฟลเดอร์ตามชื่อ Database
- ✅ ลบไฟล์เก่ากว่า 7 วันอัตโนมัติ
- ✅ ส่งแจ้งเตือนผ่าน URL (push notify)
- ✅ อัปโหลดไฟล์ขึ้น Google Drive อัตโนมัติ

---

## 📂 ตัวอย่างโครงสร้างไฟล์ Backup

```
backups/
├── db1/
│   ├── 2025-07-24.sql
│   ├── 2025-07-23.sql
├── db3/
│   ├── 2025-07-24.bak
│   └── ...
```

---

## ⚙️ การติดตั้ง

### 1. Clone Repo

```bash
$ git clone https://github.com/rx8s/py-backup-database.git
$ cd py-backup-database
```

### 2. ติดตั้งไลบรารีที่จำเป็น

```bash
$ pip3 install requests python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
### 3. เตรียม Google Drive API

- ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
- เปิดใช้งาน **Google Drive API**
- สร้าง OAuth Credentials แบบ "Desktop"
- ดาวน์โหลด `credentials.json` และวางไว้ใน root ของโปรเจกต์
- รันโปรแกรมครั้งแรกเพื่อ login และสร้าง `token.pickle`

---

## รัน manual
### 📌 Linux / macOS
```bash
$ cd /full/path/to/py-backup-database
$ python3 backup_database.py
```

### 📌 Windows
```bash
cd C:/full/path/to/py-backup-database
python3 backup_database.py
```


## 🕐 ตั้งเวลารันอัตโนมัติ (01:00 ทุกวัน)

### 📌 Linux / macOS

```bash
crontab -e
```

เพิ่มบรรทัดนี้:

```bash
0 1 * * * /usr/bin/python3 /full/path/to/backup_database.py
```

### 📌 Windows

ใช้ **Task Scheduler**:
- Trigger: Daily at 01:00
- Action: Start a program → `python`
- Arguments: `C:\full\path\to\backup_database.py`

---

## 🔧 การตั้งค่าหลัก (ใน `backup_database.py`)

```python

BACKUP_ROOT = "/your/backup/folder"  # รองรับทั้ง Linux และ Windows

MYSQL_USER = "root"
MYSQL_PASSWORD = "yourpassword"
MYSQL_DATABASES = ["db1", "db2"]

SQLSERVER_HOST = "localhost"
SQLSERVER_USER = "sa"
SQLSERVER_PASSWORD = "yourpassword"
SQLSERVER_DATABASES = ["db3", "db4"]

PUSH_URL = "https://example.com/push-msg"

```

---

## 🧠 หมายเหตุสำคัญ

- การ Backup SQL Server แบบ Daily ใช้ `BACKUP LOG` (ต้องตั้ง Recovery Model เป็น FULL)
- หากต้องการเปลี่ยนเป็น **Differential Backup** ให้แก้ `"LOG"` → `"DIFFERENTIAL"`
- Google Drive API ต้องเปิดใช้ และ Login ครั้งแรกผ่าน browser (ครั้งเดียว)

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙋 Support

หากคุณต้องการปรับแต่งเพิ่มเติม เช่น:
- ใช้ `.env` ไฟล์สำหรับเก็บ config
- ส่งแจ้งเตือนผ่าน LINE Notify
- จัดหมวดหมู่ใน Google Drive

สามารถเปิด Issue หรือ Pull Request ได้เลย 🙌
