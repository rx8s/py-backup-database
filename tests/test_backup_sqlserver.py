import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from backup_sqlserver import backup_sqlserver

class TestBackupSQLServer(unittest.TestCase):

    @patch("backup_sqlserver.ensure_dir")
    @patch("backup_sqlserver.cleanup_old_files")
    @patch("subprocess.run")
    @patch("multiprocessing.Queue")  # patch class จริง
    def test_backup_sqlserver_runs(self, mock_queue_cls, mock_run, mock_cleanup, mock_ensure):
        # สร้าง mock queue instance
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue

        # เรียกฟังก์ชัน
        backup_sqlserver(mock_queue)

        # ตรวจสอบ subprocess.run ถูกเรียก
        mock_run.assert_called()
        # ตรวจสอบ queue.put ถูกเรียก
        mock_queue.put.assert_called()
        # ตรวจสอบ ensure_dir และ cleanup_old_files ถูกเรียก
        mock_ensure.assert_called()
        mock_cleanup.assert_called()
