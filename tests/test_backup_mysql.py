import unittest
from unittest.mock import patch, MagicMock
import backup_mysql

class TestBackupMySQL(unittest.TestCase):

    @patch("backup_mysql.ensure_dir")
    @patch("backup_mysql.cleanup_old_files")
    @patch("subprocess.run")
    @patch("backup_mysql.MYSQL_DATABASES", new=["test_db"])
    def test_backup_mysql_runs(self, mock_run, mock_cleanup, mock_ensure):
        # สร้าง mock queue
        mock_queue = MagicMock()

        # เรียกฟังก์ชัน
        backup_mysql.backup_mysql(mock_queue)

        # ตรวจสอบ subprocess.run ถูกเรียก
        mock_run.assert_called()  # จะผ่าน
        # ตรวจสอบ queue.put ถูกเรียก
        mock_queue.put.assert_called()
        # ตรวจสอบ ensure_dir และ cleanup_old_files ถูกเรียก
        mock_ensure.assert_called()
        mock_cleanup.assert_called()
