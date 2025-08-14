# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from backup_sqlserver import backup_sqlserver

class TestBackupSQLServer(unittest.TestCase):

    @patch("backup_sqlserver.ensure_dir")
    @patch("backup_sqlserver.cleanup_old_files")
    @patch("subprocess.run")
    # @patch("backup_sqlserver.Queue")  # patch class จริง
    def test_backup_sqlserver_runs(self, mock_queue_cls, mock_run, mock_cleanup, mock_ensure):
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue
        backup_sqlserver(mock_queue)
        mock_run.assert_called()
        mock_queue.put.assert_called()
        mock_ensure.assert_called()
        mock_cleanup.assert_called()
