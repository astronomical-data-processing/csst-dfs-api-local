# import logging
# import unittest

# from csst_dfs_api_local.ifs import RefFitsApi

# log = logging.getLogger('csst')
# class IFSFitsTestCase(unittest.TestCase):

#     def setUp(self):
#         self.api = RefFitsApi()
#         self.api.scan2db()

#     def test_find(self):
#         path = self.api.find(obs_time=300, type='Flat')
#         log.info('find', path)
#         path = self.api.find(fits_id='CCD1_Flat_img.fits')
#         print(path)
#         log.info('find', path)
    
#     def test_read(self):
#         file = self.api.read(fits_id='CCD1_Flat_img.fits')
#         log.info('read', str(type(file)))
#         path = self.api.find(obs_time=300, type='Flat')
#         file = self.api.read(file_path=path)
#         log.info('read', str(type(file)))
