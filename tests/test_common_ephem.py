import os
import unittest
from astropy.io import fits

from csst_dfs_api_local.common.ephem import EphemSearchApi

class CommonEphemTestCase(unittest.TestCase):

    def setUp(self):
        self.api = EphemSearchApi()

    def test_gaia_query(self):
        recs = self.api.gaia_query(ra=260, dec=-27, radius=0.01, mag=0.01, limit=2)
        print('find:', recs)
