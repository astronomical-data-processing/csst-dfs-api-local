import os
import unittest
from astropy.io import fits

from csst_dfs_api_local.ifs import RefFitsApi

class IFSFitsTestCase(unittest.TestCase):

    def setUp(self):
        self.api = RefFitsApi()

    # def test_find(self):
    #     recs = self.api.find(exp_time=('2021-03-19 13:42:22', '2021-03-19 15:28:00'), ref_type=RefFitsApi.REF_FITS_FLAT)
    #     print('find:', recs)
    #     assert len(recs) > 1

    #     recs = self.api.find()
    #     print('=' * 80)
    #     print('find:', recs)
    #     assert len(recs) > 1

    # def test_read(self):
    #     recs = self.api.find(file_name='CCD2_Flat_img.fits')
    #     print("The full path: ", os.path.join(self.api.root_dir, recs[0]['file_path']))

    #     file_segments = self.api.read(file_path=recs[0]['file_path'])
    #     file_bytes = b''.join(file_segments)
    #     hdul = fits.HDUList.fromstring(file_bytes)
    #     print(hdul.info())
    #     hdr = hdul[0].header
    #     print(repr(hdr))      

    # def test_update_status(self):
    #     recs = self.api.find(file_name='CCD2_Flat_img.fits')
    #     self.api.update_status(fits_id=recs[0]['id'],status=1)
    #     rec = self.api.get(fits_id=recs[0]['id'])
    #     assert rec['status'] == 1

    # def test_write(self):
    #     recs = self.api.write(file_path='/opt/temp/csst_ifs/CCD3_Flat_img.fits')
    #     recs = self.api.find(file_name='CCD3_Flat_img.fits')
    #     rec = self.api.get(fits_id=recs[0]['id'])
    #     print(rec)
    
    def test_associate_raw(self):
        raw_fits_ids = [3,4,5]
        ref_fits_id = 2
        self.api.associate_raw(raw_fits_ids = raw_fits_ids, ref_fits_id = ref_fits_id)
