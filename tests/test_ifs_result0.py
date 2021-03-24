import os
import unittest
from astropy.io import fits

from csst_dfs_api_local.ifs import Result0Api

class IFSResult0TestCase(unittest.TestCase):

    def setUp(self):
        self.api = Result0Api()

    # def test_find(self):
    #     recs = self.api.find(file_name='CCD2_ObsTime_1200_ObsNum_40.fits')
    #     print('find:', recs)
    #     assert len(recs) == 1

    #     recs = self.api.find()
    #     print('find:', recs)
    #     assert len(recs) > 1

    # def test_read(self):
    #     recs = self.api.find(file_name='CCD2_ObsTime_1200_ObsNum_40.fits')
    #     print("The full path: ", os.path.join(self.api.root_dir, recs[0]['file_path']))

    #     file_segments = self.api.read(file_path=recs[0]['file_path'])
    #     file_bytes = b''.join(file_segments)
    #     hdul = fits.HDUList.fromstring(file_bytes)
    #     print(hdul.info())
    #     hdr = hdul[0].header
    #     print(repr(hdr))      

    def test_write(self):
        self.api.write(raw_id = 1, 
                file_path='/opt/temp/csst_ifs/CCD2_ObsTime_1200_ObsNum_40.fits',
                proc_type = 'default')

        recs = self.api.find(raw_id=1)
        print()
        print(recs)
        print("="*80)
        recs = self.api.find(file_name='CCD2_ObsTime_1200_ObsNum_40.fits')
        print(recs)
