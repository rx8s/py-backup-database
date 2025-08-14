import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from backup_sqlserver import backup_sqlserver

class TestBackupSQLServer(unittest.TestCase):

    @patch("backup_sqlserver.subprocess.run")
    @patch("backup_sqlserver.Queue")
    def test_backup_sqlserver_runs(self, mock_queue_class, mock_subprocess):
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        mock_subprocess.return_value.returncode = 0

        backup_sqlserver(mock_queue)

        self.assertTrue(mock_subprocess.called)
        self.assertTrue(mock_queue.put.called)

if __name__ == "__main__":
    unittest.main()
