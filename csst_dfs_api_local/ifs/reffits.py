import logging
import os
import shutil

from astropy.io import fits

from ..common.db import DBClient
from ..common.utils import get_parameter
from . import FitsApi

log = logging.getLogger('csst')


class RefFitsApi(FitsApi):
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
        name = basename.split('.fits')[0]
        c, r = self.db.select_many(
            "select * from t_rawfits where id=?",
            (name,)
        )
        if len(r) >= 1:
            print('already upload', name)
            return
        
        hu = fits.getheader(file_path)
        obs_time = hu['obst']
        ccd_num = hu['ccd_num']
        type = name.split('_')[1]
        save_path = os.path.join(self.root_dir, 'refs')
        save_path = os.path.join(save_path, basename)

        self.db.execute(
            'INSERT INTO t_rawfits VALUES(?,?,?,?,?)',
            (basename, obs_time, ccd_num, type, save_path)
        )
        self.db._conn.commit()
        if file_path != save_path:
            shutil.copyfile(file_path, save_path)
        log.info("%s imported.", save_path)

    def scan2db(self):
        paths = {}

        for (path, _, file_names) in os.walk(os.path.join(self.root_dir, "refs")):
            for filename in file_names:
                if filename.find(".fits") > 0:
                    self.upload(file_path=os.path.join(path, filename))
        return paths
