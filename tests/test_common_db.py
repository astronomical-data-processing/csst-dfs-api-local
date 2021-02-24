import unittest

from csst_dfs_api_local.common.db import DBClient

class DBClientTestCase(unittest.TestCase):
    def setUp(self):
        self.db_path = "/opt/temp/csst"

    def test_db_init(self):
        db = DBClient()
        db.select_one("select * from t_rawfits")
    
