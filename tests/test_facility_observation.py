import unittest

from csst_dfs_api_local.facility.observation import ObservationApi

class FacilityObservationTestCase(unittest.TestCase):

    def setUp(self):
        self.api = ObservationApi()

    def test_find(self):
        recs = self.api.find(module_id="MSC",limit = 0)
        print('find:', recs)

    def test_get(self):
        rec = self.api.get(obs_id=11)
        print('get:', rec)

    def test_update_proc_status(self):
        rec = self.api.update_proc_status(obs_id = 11, status = 3, )
        print('update_proc_status:', rec)

    def test_update_qc0_status(self):
        rec = self.api.update_qc0_status(obs_id = 11, status = 3, )
        print('update_qc0_status:', rec)        

    def test_write(self):
        rec = self.api.write(
            obs_time = "2021-06-06 11:12:13",
            exp_time = 150,
            module_id = "MSC",
            obs_type = "sci",
            facility_status_id = 3,
            module_status_id = 3)
        print('write:', rec)