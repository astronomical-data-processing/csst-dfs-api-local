import unittest
from astropy.io import fits

from csst_dfs_api_local.ifs import FitsApi

class IFSFitsTestCase(unittest.TestCase):

    def setUp(self):
        self.api = FitsApi()

    def test_find(self):
        recs = self.api.find(file_name='CCD1_ObsTime_300_ObsNum_7.fits')
        print('find:', recs)
        assert len(recs) == 1

        recs = self.api.find()
        print('find:', recs)
        assert len(recs) > 1

    def test_read(self):
        recs = self.api.find(file_name='CCD1_ObsTime_300_ObsNum_7.fits')
        print("The full path: ", os.path.join(self.api.root_dir, recs[0]['file_path']))

        file_segments = self.api.read(file_path=recs[0]['file_path'])
        file_bytes = b''.join(file_segments)
        hdul = fits.HDUList.fromstring(file_bytes)
        print(hdul.info())
        hdr = hdul[0].header
        print(repr(hdr))      

    def test_update_proc_status(self):
        recs = self.api.find(file_name='CCD1_ObsTime_300_ObsNum_7.fits')

        self.api.update_proc_status(fits_id=recs[0]['id'],status=1)

        rec = self.api.get(fits_id=recs[0]['id'])
        assert rec['prc_status'] == 1

    def test_update_qc0_status(self):
        recs = self.api.find(file_name='CCD1_ObsTime_300_ObsNum_7.fits')

        self.api.update_qc0_status(fits_id=recs[0]['id'],status=1)

        rec = self.api.get(fits_id=recs[0]['id'])
        assert rec['qc0_status'] == 1

    def test_write(self):
        recs = self.api.write(file_path='/opt/temp/csst_ifs/CCD2_ObsTime_1200_ObsNum_40.fits')

        recs = self.api.find(file_name='CCD2_ObsTime_1200_ObsNum_40.fits')

        rec = self.api.get(fits_id=recs[0]['id'])

        print(rec)