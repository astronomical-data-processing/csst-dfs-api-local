import os
import unittest
from astropy.io import fits

from csst_dfs_api_local.facility.calmerge import CalMergeApi

class CalMergeApiTestCase(unittest.TestCase):

    def setUp(self):
        self.api = CalMergeApi()

    def test_find(self):
        recs = self.api.find(detector_no='CCD01',
            ref_type = "bias",
            obs_time = ("2021-06-01 11:12:13","2021-06-08 11:12:13"))
        print('find:', recs)

    def test_get(self):
        rec = self.api.get(id = 3)
        print('get:', rec)

    def test_update_proc_status(self):
        rec = self.api.update_proc_status(id = 3, status = 1)
        print('update_proc_status:', rec)

    def test_update_qc1_status(self):
        rec = self.api.update_qc1_status(id = 3, status = 2)
        print('update_qc1_status:', rec)    

    def test_write(self):
        rec = self.api.write(detector_no='CCD01', 
            ref_type = "bias",
            obs_time = "2021-06-04 11:12:13",
            exp_time = 150,
            filename = "/opt/dddasd.params",
            file_path = "/opt/dddasd.fits",
            prc_status = 3,
            prc_time = '2021-06-04 11:12:13',
            level0_ids = [1,2,3,4])
        print('write:', rec)