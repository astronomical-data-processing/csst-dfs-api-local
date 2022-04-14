import os
import unittest
from astropy.io import fits

from csst_dfs_api_local.msc.level2catalog import Level2CatalogApi

class MSCLevel2CatalogApiTestCase(unittest.TestCase):

    def setUp(self):
        self.api = Level2CatalogApi()

    def test_find(self):
        recs = self.api.find(
            obs_id='100000000',
            obs_time = ("2021-05-24 11:12:13","2021-05-25 13:12:13"),
            limit = 100)
        print('find:', recs)

    def test_write(self):
        rec = self.api.write([])
        print('write:', rec)