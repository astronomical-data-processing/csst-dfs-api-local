import unittest

from csst_dfs_api_local.common.db import DBClient

class DBClientTestCase(unittest.TestCase):
    def setUp(self):
        self.db_path = "/opt/temp/csst"

    def test_db_init(self):
        db = DBClient()
        
        r = db.select_one("select date('now')")
        if r is not None:
            print("now:", r)

        r = db.exists("select * from t_observation where id=2323")
        if r:
            print("existed")
        else:
            print("not existed")

    
