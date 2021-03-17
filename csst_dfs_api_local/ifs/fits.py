
import logging
import os
import shutil
from glob import glob

from astropy.io import fits

from ..common.db import DBClient
from ..common.utils import get_parameter

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
        # if not os.path.exists(os.path.join(self.root_dir, "fits")):
        #     os.mkdir(os.path.join(self.root_dir, "fits"))
        # if not os.path.exists(os.path.join(self.root_dir, "refs")):
        #     os.mkdir(os.path.join(self.root_dir, "refs"))
        # if not os.path.exists(os.path.join(self.root_dir, "results")):
        #     os.mkdir(os.path.join(self.root_dir, "results"))

    def find(self, **kwargs):
        '''
        parameter kwargs:
        obs_time = [int]
        type = [str]
        fits_id = [str]

        return list of paths
        '''
        paths = []
        
        obs_time = get_parameter(kwargs, "obs_time")
        type = get_parameter(kwargs, "type")
        fits_id = get_parameter(kwargs, "fits_id")

        if (obs_time is None or type is None) and fits_id is None:
            raise Exception('obs_time and type need to be defind')

        if fits_id is None:
            c, r = self.db.select_many(
                'select * from t_rawfits where obs_time=? and type=?',
                (obs_time, type)
            )
            if len(r) < 1:
                raise Exception('not found')
            for items in r:
                paths.append(os.path.join(self.root_dir, items['path']))
        else:
            c, r = self.db.select_many(
                'select * from t_rawfits where id=?',
                (fits_id,),
            )
            if len(r) < 1:
                raise Exception('not found')
            return os.path.join(self.root_dir, r[0]['path'])
        return paths

    def read(self, **kwargs):
        '''
        parameter kwargs:
        fits_id = [str] 
        file_path = [str] 
        chunk_size = [int]

        yield bytes of fits file
        '''
        fits_id = get_parameter(kwargs, "fits_id")
        file_path = get_parameter(kwargs, "file_path")

        if fits_id is None and file_path is None:
            raise Exception("fits_id or file_path need to be defined")

        if fits_id is not None:
            c, r = self.db.select_one(
                "select * from t_rawfits where id=?", (fits_id))
            if c == 1:
                file_path = os.path.join(self.root_dir, r["path"])

        if file_path is not None:
            path = os.path.join(self.root_dir, file_path)
            chunk_size = get_parameter(kwargs, "chunk_size", 1024)
            with open(path, 'r') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    yield data

    def update_status(self, **kwargs):
        pass

    def upload(self, **kwargs):
        '''
        parameter kwargs:
        file_path = [str]

        upload to database and copy to csstpath
        '''
        file_path = get_parameter(kwargs, "file_path")

        if file_path is None:
            raise Exception("file_path need to be defined")

        basename = os.path.basename(file_path)
        name = basename.split('.fits')[0].lower()
        c, r = self.db.select_many(
            "select * from t_rawfits where id=?",
            (name,)
        )
        if len(r) >= 1:
            print('already upload', basename)
            return

        hu = fits.getheader(os.path.join(self.root_dir, file_path))
        obs_time = hu['obst'] if 'obst' in hu else 0
        ccd_num = hu['ccd_num'] if 'ccd_num' in hu else 0
        # print(obs_time, ccd_num)
        if 'obs' in name:
            type = 'obs'
        elif 'flat' in name:
            type = 'flat'
        elif 'bias' in name:
            type = 'bias'
        elif 'hgar' in name:
            type = 'arc'
        elif 'sky' in name:
            type = 'sky'
        else:
            type = 'None'
        

        self.db.execute(
            'INSERT INTO t_rawfits VALUES(?,?,?,?,?)',
            (basename, obs_time, ccd_num, type, file_path)
        )
        self.db._conn.commit()
        log.info("%s imported.", file_path)

    def scan2db(self):
        paths = {}

        for (path, _, file_names) in os.walk(self.root_dir):
            for filename in file_names:
                if filename.find(".fits") > 0:
                    filename = os.path.join(path, filename)
                    self.upload(file_path=filename.replace(self.root_dir, ''))
        return paths
