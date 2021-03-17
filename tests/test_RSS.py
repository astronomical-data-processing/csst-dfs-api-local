import logging
import unittest
import os

from csst_dfs_api_local.entity import RSS

log = logging.getLogger('csst')
class RSS_TestCase(unittest.TestCase):
    def setUp(self):
        self.rss = RSS('CCD1_ObsTime_600_ObsNum_30.fits')
        self.rss.set_bias()
        self.rss.set_flat(flat_file='Flat_flux.fits')
        self.rss.set_arc(arc_file='HgAr_flux.fits')
        self.rss.set_sky(sky_file='sky_noise_With_wavelength.fits')

    def test_init(self):
        assert self.rss.raw
    
    # def test_bias(self):
    #     self.rss.set_bias()
    #     assert self.rss.bias

    def test_flat(self):
        assert self.rss.flat

    def test_arc(self):
        assert self.rss.arc

    def test_sky(self):
        assert self.rss.sky

    def test_makecube(self):
        self.rss.makecube('rss_demo.pkl')
        assert os.path.exists('rss_demo.pkl')
        os.remove('rss_demo.pkl')