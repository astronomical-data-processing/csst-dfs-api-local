import os
import unittest
from astropy.io import fits

from csst_dfs_api_local.facility.calmerge import CalMergeApi

class CalMergeApiTestCase(unittest.TestCase):

    def setUp(self):
        self.api = CalMergeApi()

    def test_find(self):
        recs = self.api.find(detector_no='01',
            ref_type = "bias",
            obs_time = ("2021-06-01 11:12:13","2021-06-08 11:12:13"))
        print('find:', recs)

    def test_get_latest_by_l0(self):
        rec = self.api.get_latest_by_l0(level0_id='000001301', ref_type = "bias")
        print('get:', rec)

    def test_get(self):
        rec = self.api.get(cal_id='0000231')
        print('get:', rec)

    def test_update_proc_status(self):
        rec = self.api.update_proc_status(id = 1, status = 1)
        print('update_proc_status:', rec)

    def test_update_qc1_status(self):
        rec = self.api.update_qc1_status(id = 1, status = 2)
        print('update_qc1_status:', rec)    

    def test_write(self):
        rec = self.api.write(
            cal_id='0000231',
            detector_no='01', 
            ref_type = "bias",
            obs_time = "2021-06-04 11:12:13",
            exp_time = 150,
            filename = "/opt/dddasd.params",
            file_path = "/opt/dddasd.fits",
            prc_status = 3,
            prc_time = '2021-06-04 11:12:13',
            level0_ids = ['0000231','0000232','0000233','0000234'])
        print('write:', rec)