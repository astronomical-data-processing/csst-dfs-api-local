import logging
import unittest
import os

from csst_dfs_api_local.ifs import ingest

log = logging.getLogger('csst')
class IFSIngestTestCase(unittest.TestCase):

    def setUp(self):
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")

    def test_ingest(self):
       ingest()

