import os
import numpy as np
import pandas as pd
import logging
from astropy.io import fits

from csst_dfs_api_local.ifs import FitsApi, RefFitsApi, Result0Api, Result1Api

log = logging.getLogger('csst')

class RSS(object):

    def __init__(self, file_name):
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.fitsApi = FitsApi()
        self.refFitsApi = RefFitsApi()
        self.result0Api = Result0Api()
        self.result1Api = Result1Api()
        
        try:
            self.raw = self.fitsApi.find(file_name=file_name)
            self.raw = self.raw[0] if self.raw else None

            if self.raw is None:
                log.error('raw %s not found' %(file_name,))
        except Exception as e:
            log.error('raw %s not found' %(file_name,),e)

    def set_bias(self, file_name=None):
        try:
            self.bias = self.refFitsApi.find(file_name=file_name, ref_type=RefFitsApi.REF_FITS_BIAS)
            self.bias = self.bias[0] if self.bias else None

            if self.bias is None:
                log.error('bias %s not found' %(file_name,))
        except Exception as e:
            log.error('bias %s not found' %(file_name,),e)

    def set_flat(self, file_name=None):
        try:
            self.flat = self.refFitsApi.find(file_name=file_name, ref_type=RefFitsApi.REF_FITS_FLAT)
            self.flat = self.flat[0] if self.flat else None

            if self.flat is None:
                log.error('flat %s not found' %(file_name,))
        except Exception as e:
            log.error('flat %s not found' %(file_name,),e)

    def set_arc(self, file_name = None):
        try:
            self.arc = self.refFitsApi.find(file_name=file_name, ref_type=RefFitsApi.REF_FITS_ARC)
            self.arc = self.arc[0] if self.arc else None

            if self.arc is None:
                log.error('arc %s not found' %(file_name,))
        except Exception as e:
            log.error('arc %s not found' %(file_name,),e)

    def set_sky(self, file_name = None):
        try:
            self.sky = self.refFitsApi.find(file_name=file_name, ref_type=RefFitsApi.REF_FITS_SKY)
            self.sky = self.sky[0] if self.sky else None

            if self.sky is None:
                log.error('sky %s not found' %(file_name,))
        except Exception as e:
            log.error('sky %s not found' %(file_name,),e)

    def makecube(self, outfile):

        hdul_raw = fits.open(os.path.join(self.root_dir, self.raw['file_path']))

        hdul_arc = fits.open(os.path.join(self.root_dir, self.arc['file_path']))
        hdul_flat = fits.open(os.path.join(self.root_dir, self.flat['file_path']))
        hdul_sky  = fits.open(os.path.join(self.root_dir, self.sky['file_path']))

        hdul_raw.append(hdul_arc[0])
        hdul_raw.append(hdul_flat[0])
        hdul_raw.append(hdul_sky[0])

        hdul_raw.writeto(outfile, overwrite=True)

        self.result0Api.write(raw_id = self.raw['id'], file_path = outfile, proc_type = 'default')

    def makecube2(self, outfile):
        refiles = [self.raw, self.arc, self.flat, self.bias, self.sky]

        raw_segments = self.fitsApi.read(self.raw['id'])
        arc_segments = self.refFitsApi.read(self.arc['id'])
        flat_segments = self.refFitsApi.read(self.flat['id'])
        sky_segments = self.refFitsApi.read(self.sky['id'])

        hdul_raw = fits.HDUList.fromstring(b''.join(raw_segments))
        hdul_arc = fits.HDUList.fromstring(b''.join(arc_segments))
        hdul_flat = fits.HDUList.fromstring(b''.join(flat_segments))
        hdul_sky = fits.HDUList.fromstring(b''.join(sky_segments))

        hdul_raw.append(hdul_arc[0])
        hdul_raw.append(hdul_flat[0])
        hdul_raw.append(hdul_sky[0])

        hdul_raw.writeto(outfile, overwrite=True)

        self.result0Api.write(raw_id = self.raw['id'], file_path = outfile, proc_type = 'default')

if __name__ == '__main__':
    rss1 = RSS('CCD1_ObsTime_300_ObsNum_1.fits')               # raw data
    # rss1.set_bias()                                             # currently no Bias file
    rss1.set_flat(file_name = 'Flat_flux.fits')                 # flat file
    rss1.set_arc(file_name = 'HgAr_flux.fits')                  # arc file
    rss1.set_sky(file_name = 'sky_noise_With_wavelength.fits')  # sky file

    rss1.makecube('/opt/temp/csst_ifs/rss_demo.fits')
