import logging
import unittest

from csst_dfs_api_local.ifs import FitsApi

log = logging.getLogger('csst')
class IFSFitsTestCase(unittest.TestCase):

    def setUp(self):
        self.api = FitsApi()
        self.api.scan2db()

    def test_find(self):
        path = self.api.find(obs_time=900, type='obs')
        log.info('find', path)
        path = self.api.find(fits_id='CCD2_ObsTime_600_ObsNum_8')
        log.info('find', path)
    
    def test_read(self):
        file = self.api.read(fits_id='CCD2_ObsTime_600_ObsNum_8')
        log.info('read', str(type(file)))
        path = self.api.find(obs_time=900, type='obs')
        file = self.api.read(file_path=path)
        log.info('read', str(type(file)))
