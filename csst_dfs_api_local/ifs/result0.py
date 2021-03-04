import logging

log = logging.getLogger('csst')
class Result0Api(object):
    def __init__(self, sub_system = "ifs"):
        self.sub_system = sub_system
    
    def upload(self, **kwargs):
        '''
        parameter kwargs:
        fits_id = [str] 
        file_path = [str] 
        chunk_size = [int]

        yield bytes of fits file
        '''
        pass
    
    def find(self, **kwargs):
        pass

    def read(self, **kwargs):
        pass

    def wirte(self, **kwargs):
        pass