import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from backup_mysql import backup_mysql

class TestBackupMySQL(unittest.TestCase):

    @patch("backup_mysql.subprocess.run")
    @patch("backup_mysql.Queue")
    def test_backup_mysql_runs(self, mock_queue_class, mock_subprocess):
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        # Mock subprocess.run ให้ไม่รันจริง
        mock_subprocess.return_value.returncode = 0

        # เรียกฟังก์ชัน
        backup_mysql(mock_queue)

        # ตรวจสอบว่า subprocess.run ถูกเรียก
        self.assertTrue(mock_subprocess.called)
        self.assertTrue(mock_queue.put.called)

if __name__ == "__main__":
    unittest.main()
