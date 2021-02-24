
import os
import logging
from ..common.utils import get_parameter
from ..common.db import DBClient

log = logging.getLogger('csst')

class FitsApi(object):
    def __init__(self):
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.check_dir()
        self.db = DBClient()

    def check_dir(self):
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)
            log.info("using [%s] as root directory", self.root_dir)
        if not os.path.exists(os.path.join(self.root_dir, "fits")):
            os.mkdir(os.path.join(self.root_dir, "fits"))
        if not os.path.exists(os.path.join(self.root_dir, "refs")):
            os.mkdir(os.path.join(self.root_dir, "refs"))
        if not os.path.exists(os.path.join(self.root_dir, "results")):
            os.mkdir(os.path.join(self.root_dir, "results"))

    def find(self, **kwargs):
        '''
        parameter kwargs:
        obs_time = [str] 

        return list of fits_id
        '''
        paths = {}
        for (path, _, file_names) in os.walk(os.path.join(self.root_dir, "fits")):
            for filename in file_names:
                if filename.find(".fits") > 0:
                    paths[filename] = os.path.join(path, filename)
        return paths

    def read(self, **kwargs):
        '''
        parameter kwargs:
        fits_id = [str] 
        file_path = [str] 
        
        yield bytes of fits file
        '''
        fits_id = get_parameter(kwargs, "fits_id")
        file_path = get_parameter(kwargs, "file_path")

        if fits_id is None and file_path is None:
            raise Exception("fits_id or file_path need to be defined")

        if fits_id is not None:
            c, r = self.db.select_one("select * from t_rawfits where id=?",(fits_id))
            if c == 1:
                file_path = r["path"]

        if file_path is not None:
            chunk_size = get_parameter(kwargs, "chunk_size", 1024)
            with open(file_path,'r') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    yield data
        

    def update_status(self, **kwargs):
        pass    

    def upload(self,**kwargs): 
        pass

    def scan2db(self):
        paths = {}
        
        for (path, _, file_names) in os.walk(os.path.join(self.root_dir, "fits")):
            for filename in file_names:
                if filename.find(".fits") > 0:
                    obs_time = ""
                    self.db.execute("insert into t_rawfits values(?,?,?)", param=(filename, obs_time, os.path.join(path, filename)))
                    log.info("%s imported.",os.path.join(path, filename))
        return paths