import logging
import unittest
import os

from csst_dfs_api_local.ifs import FitsApi

log = logging.getLogger('csst')
class IFSFitsTestCase(unittest.TestCase):

    def setUp(self):
        self.api = FitsApi()
        # self.api.scan2db()

    def test_find(self):
        path1 = self.api.find(obs_time=900, type='obs')
        log.info('find', path1)
        assert len(path1) > 0
        path2 = self.api.find(fits_id='CCD2_ObsTime_600_ObsNum_8.fits')
        log.info('find', path2)
        assert 'CCD2_ObsTime_600_ObsNum_8.fits' in path2

    
    def test_read(self):
        file = self.api.read(fits_id='CCD2_ObsTime_600_ObsNum_8.fits')
        log.info('read', str(type(file)))
        path = self.api.find(obs_time=900, type='obs')
        file = self.api.read(file_path=path)
        log.info('read', str(type(file)))
