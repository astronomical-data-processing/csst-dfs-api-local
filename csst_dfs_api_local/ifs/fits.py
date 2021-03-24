
import logging
import os
from os.path import join
import shutil
import time, datetime
import shutil

from glob import glob

from astropy.io import fits

from ..common.db import DBClient
from ..common.utils import *

log = logging.getLogger('csst')
class FitsApi(object):
    def __init__(self, sub_system = "ifs"):
        self.sub_system = sub_system
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
            obs_time = [int],
            file_name = [str],
            exp_time = (start, end),
            ccd_num = [int],
            qc0_status = [int],
            prc_status = [int]

        return list of raw records
        '''
        paths = []
        
        obs_time = get_parameter(kwargs, "obs_time")
        file_name = get_parameter(kwargs, "file_name")
        exp_time = get_parameter(kwargs, "exp_time", (None, format_time_ms(time.time())))
        ccd_num = get_parameter(kwargs, "ccd_num")
        qc0_status = get_parameter(kwargs, "qc0_status")
        prc_status = get_parameter(kwargs, "prc_status")
        
        sql = []

        sql.append("select * from ifs_rawfits where exp_time<='" + exp_time[1]+"'")

        if exp_time[0] is not None:
            sql.append(" and exp_time>='" + exp_time[0] + "'")
        if obs_time is not None:
            sql.append(" and obs_time=" + obs_time)
        if ccd_num is not None:
            sql.append(" and ccd_num=" + ccd_num)
        if qc0_status is not None:
            sql.append(" and qc0_status=" + qc0_status) 
        if prc_status is not None:
            sql.append(" and prc_status=" + prc_status)
        
        if file_name:
            sql = ["select * from ifs_rawfits where filename='" + file_name + "'"]
        _, r = self.db.select_many("".join(sql))

        return r

    def get(self, **kwargs):
        '''
        parameter kwargs:
            fits_id = [int] 

        return dict or None
        '''
        fits_id = get_parameter(kwargs, "fits_id", -1)
        r = self.db.select_one(
            "select * from ifs_rawfits where id=?", (fits_id,))
        return r

    def read(self, **kwargs):
        '''
        parameter kwargs:
            fits_id = [int],
            file_path = [str], 
            chunk_size = [int] default 20480

        yield bytes of fits file
        '''
        fits_id = get_parameter(kwargs, "fits_id")
        file_path = get_parameter(kwargs, "file_path")

        if fits_id is None and file_path is None:
            raise Exception("fits_id or file_path need to be defined")

        if fits_id is not None:
            r = self.db.select_one(
                "select * from ifs_rawfits where id=?", (fits_id,))
            if r is not None:
                file_path = r["file_path"]

        if file_path is not None:
            chunk_size = get_parameter(kwargs, "chunk_size", 20480)
            return yield_file_bytes(os.path.join(self.root_dir, file_path), chunk_size)

    def update_proc_status(self, **kwargs):
        '''
        parameter kwargs:
            fits_id = [int],
            status = [int]
        '''
        fits_id = get_parameter(kwargs, "fits_id")
        status = get_parameter(kwargs, "status")

        existed = self.db.exists(
            "select * from ifs_rawfits where id=?",
            (fits_id,)
        )
        if not existed:
            log.warning('%s not found' %(fits_id, ))
            return
        self.db.execute(
            'update ifs_rawfits set prc_status=?, prc_time=? where id=?',
            (status, format_time_ms(time.time()), fits_id)
        )  
        self.db.end() 

    def update_qc0_status(self, **kwargs):
        '''
        parameter kwargs:
            fits_id = [int],
            status = [int]
        '''

        fits_id = get_parameter(kwargs, "fits_id")
        status = get_parameter(kwargs, "status")

        existed = self.db.exists(
            "select * from ifs_rawfits where id=?",
            (fits_id,)
        )
        if not existed:
            log.warning('%s not found' %(fits_id, ))
            return
        self.db.execute(
            'update ifs_rawfits set qc0_status=?, qc0_time=? where id=?',
            (status, format_time_ms(time.time()), fits_id)
        )  
        self.db.end() 

    def import2db(self, **kwargs):
        '''
        reduce the header of fits file of server and insert a record into database
        parameter kwargs:
            file_path = [str]
        '''
        file_path = get_parameter(kwargs, "file_path")

        if file_path is None:
            raise Exception("file_path need to be defined")
        
        file_full_path = os.path.join(self.root_dir, file_path)

        if not os.path.exists(file_full_path):
            raise Exception("%s not found" % (file_full_path))

        file_name = os.path.basename(file_path)

        existed = self.db.exists(
            "select * from ifs_rawfits where filename=?",
            (file_name,)
        )
        if existed:
            log.warning('%s has already been imported' %(file_path, ))
            return

        hu = fits.getheader(file_full_path)
        obs_time = hu['obst'] if 'obst' in hu else '1'
        ccd_num = hu['ccd_num'] if 'ccd_num' in hu else 0
        exp_time = format_time_ms(time.time())

        self.db.execute(
            'INSERT INTO ifs_rawfits (filename, obs_time, ccd_num, exp_time, file_path, qc0_status, prc_status, create_time) \
                VALUES (?,?,?,?,?,?,?,?)',
            (file_name, obs_time, ccd_num, exp_time, file_path, 0,  0, format_time_ms(time.time()),)
        )
        self.db.end()

        log.info("raw fits %s imported.", file_path)

    def write(self, **kwargs):
        '''
        copy a local file to file storage, then reduce the header of fits file and insert a record into database
        parameter kwargs:
            file_path = [str]
        '''        
        file_path = get_parameter(kwargs, "file_path")

        if not file_path:
            log.error("file_path is None")
            return

        new_file_dir = create_dir(os.path.join(self.root_dir, "fits"),
                self.sub_system, 
                "/".join([str(datetime.now().year),"%02d"%(datetime.now().month),"%02d"%(datetime.now().day)]))

        file_basename = os.path.basename(file_path)
        new_file_path = os.path.join(new_file_dir, file_basename)
        shutil.copyfile(file_path, new_file_path)

        self.import2db(file_path = new_file_path.replace(self.root_dir, '')[1:])