import unittest

from csst_dfs_api_local.sls import Level0DataApi

class SLSLevel0DataApiTestCase(unittest.TestCase):

    def setUp(self):
        self.api = Level0DataApi()

    def test_find(self):
        recs = self.api.find(obs_id = '300000055', obs_type = 'sky', limit = 0)
        print('find:', recs)

    def test_get(self):
        rec = self.api.get(id = 31)
        print('get:', rec)

    def test_update_proc_status(self):
        rec = self.api.update_proc_status(id = 31, status = 6)
        print('update_proc_status:', rec)

    def test_update_qc0_status(self):
        rec = self.api.update_qc0_status(id = 31, status = 7)
        print('update_qc0_status:', rec)

    def test_write(self):
        rec = self.api.write(
            obs_id = '0000013',
            detector_no = "01",
            obs_type = "sky",            
            obs_time = "2021-06-06 11:12:13",
            exp_time = 150,
            detector_status_id = 3,
            filename = "MSC_00001234",
            file_path = "/opt/MSC_00001234.fits")
        print('write:', rec)  
