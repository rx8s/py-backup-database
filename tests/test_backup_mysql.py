import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from backup_mysql import backup_mysql

class TestBackupMySQL(unittest.TestCase):

    @patch("backup_mysql.ensure_dir")
    @patch("backup_mysql.cleanup_old_files")
    @patch("subprocess.run")
    @patch("backup_mysql.Queue")  # patch ถูกต้องตาม namespace ของ backup_mysql
    def test_backup_mysql_runs(self, mock_queue_cls, mock_run, mock_cleanup, mock_ensure):
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue
        backup_mysql(mock_queue)
        mock_run.assert_called()
        mock_queue.put.assert_called()
        mock_ensure.assert_called()
        mock_cleanup.assert_called()
