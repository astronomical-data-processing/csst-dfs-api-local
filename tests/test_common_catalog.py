import os
import unittest
from astropy.io import fits

from csst_dfs_api_local.common.catalog import CatalogApi

class CommonEphemTestCase(unittest.TestCase):

    def setUp(self):
        self.api = CatalogApi()

    def test_gaia3_query(self):
        result = self.api.gaia3_query(ra=56.234, dec=14.4665, radius=1, min_mag=-1, max_mag=-1, obstime=-1, limit=2)
        print('return:', result)