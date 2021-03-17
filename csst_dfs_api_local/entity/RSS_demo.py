import os

import numpy as np
import pandas as pd
from csst_dfs_api_local.ifs import FitsApi


class RSS():

    def __init__(self, rawdata):
        self.fitsapi = FitsApi()
        try:
            self.raw = self.fitsapi.find(fits_id=rawdata)
            if not os.path.exists(self.raw):
                print(self.raw, 'does not exist')
                self.raw = False
        except:
            print(rawdata, 'not in database')
            self.raw = False

    def set_bias(self, bias_file=None):
        try:
            self.bias = self.fitsapi.find(fits_id=bias_file)
            if not os.path.exists(self.bias):
                print(self.bias, 'does not exist')
                self.bias = False
        except:
            print(bias_file, 'not in database')
            self.bias = False

    def set_flat(self, flat_file=None):
        try:
            self.flat = self.fitsapi.find(fits_id=flat_file)
            if not os.path.exists(self.flat):
                print(self.flat, 'does not exist')
                self.flat = False
        except:
            print(flat_file, 'not in database')
            self.flat = False

    def set_arc(self, arc_file=None):
        try:
            self.arc = self.fitsapi.find(fits_id=arc_file)
            if not os.path.exists(self.arc):
                print(self.arc, 'does not exist')
                self.arc = False
        except:
            print(arc_file, 'not in database')
            self.arc = False

    def set_sky(self, sky_file=None):
        try:
            self.sky = self.fitsapi.find(fits_id=sky_file)
            if not os.path.exists(self.sky):
                print(self.sky, 'does not exist')
                self.sky = False
        except:
            print(sky_file, 'not in database')
            self.sky = False

    def makecube(self, outfile):

        refiles = [self.raw, self.arc, self.flat, self.bias, self.sky]
        print('reference files: ', refiles)
        df = pd.DataFrame(refiles)

        df.to_pickle(outfile)


if __name__ == '__main__':

    rss1 = RSS('CCD1_ObsTime_600_ObsNum_30.fits')     # raw data

    rss1.bias()                                     # currently no Bias file
    rss1.flat(flat_file='Flat_flux.fits')           # flat file
    rss1.arc(arc_file='HgAr_flux.fits')             # arc file
    rss1.sky(sky_file='sky_noise_With_wavelength.fits')  # sky file

    rss1.makecube('rss_demo.pkl')
