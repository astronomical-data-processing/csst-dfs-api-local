import unittest

from csst_dfs_api_local.sls import Level2SpectraApi

class SLSLevel2SpectraTestCase(unittest.TestCase):

    def setUp(self):
        self.api = Level2SpectraApi()

    def test_find(self):
        recs = self.api.find(
                level1_id=1, 
                create_time = ("2021-06-01 11:12:13","2021-06-08 11:12:13")
            )
        print('find:', recs)

    def test_get(self):
        rec = self.api.get(id = 1)
        print('get:', rec)

    def test_update_proc_status(self):
        rec = self.api.update_proc_status(id = 1, status = 4)
        print('update_proc_status:', rec)

    def test_update_qc1_status(self):
        rec = self.api.update_qc1_status(id = 1, status = 7)
        print('update_qc1_status:', rec)

    def test_write(self):
        rec = self.api.write(
            level1_id=2, 
            spectra_id = "222",
            region = "[12,13,24,24]",
            prc_status = 3,
            prc_time = '2021-06-05 11:12:13',
            filename = "dddasd223234.fits",
            file_path = "/opt/dddasd23.fits",
            pipeline_id = "P2")
        print('write:', rec)