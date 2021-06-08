import unittest

from csst_dfs_api_local.facility.detector import DetectorApi

class DetectorApiTestCase(unittest.TestCase):

    def setUp(self):
        self.api = DetectorApi()

    def test_find(self):
        recs = self.api.find(module_id = 'MSC')
        print('find:', recs)

    def test_get(self):
        rec = self.api.get(no = 'CCD01')
        print('get:', rec)

    def test_write(self):
        rec = self.api.write(no = 'CCD02', 
                detector_name = 'CCD02', 
                module_id = 'MSC', 
                filter_id='f2')
        print('write:', rec)

    def test_update(self):
        rec = self.api.update(no = 'CCD01', filter_id = 'f1')
        print('update:', rec)

    def test_delete(self):
        rec = self.api.delete(no = 'CCD01')
        print('delete:', rec)

    def test_find_status(self):
        recs = self.api.find_status(detector_no = 'CCD01', 
            status_occur_time = ('2021-06-02','2021-06-08'), 
            limit = 0)
        print('find status:', recs)

    def test_get_status(self):
        rec = self.api.get_status(id = 2)
        print('get status:', rec)

    def test_write_status(self):
        rec = self.api.write_status(detector_no = 'CCD01', status = '{........}',status_time='2021-06-05 12:12:13')
        print('write status:', rec)