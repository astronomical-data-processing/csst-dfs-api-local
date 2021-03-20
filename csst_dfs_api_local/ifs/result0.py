import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *

log = logging.getLogger('csst')

class Result0Api(object):
    def __init__(self, sub_system = "ifs"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.check_dir()
        self.db = DBClient()

    def check_dir(self):
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)
            log.info("using [%s] as root directory", self.root_dir)

        if not os.path.exists(os.path.join(self.root_dir, "results0")):
            os.mkdir(os.path.join(self.root_dir, "results0")) 

    def find(self, **kwargs):
        '''
        parameter kwargs:
            raw_id = [int],
            file_name = [str],
            proc_type = [str]

        return list of level 0 record
        '''
        paths = []
        
        raw_id = get_parameter(kwargs, "raw_id", -1)
        file_name = get_parameter(kwargs, "file_name")
        proc_type = get_parameter(kwargs, "proc_type")
        sql = []

        sql.append("select * from ifs_result_0 where raw_id=%d" %(raw_id,))

        if proc_type is not None:
            sql.append(" and proc_type='" + proc_type + "'")

        if file_name:
            sql = ["select * from ifs_result_0 where filename='" + file_name + "'"]

        _, r = self.db.select_many("".join(sql))

        return r
        
    def get(self, **kwargs):
        ''' query database, return a record as dict

        parameter kwargs:
            fits_id = [int] 

        return dict or None
        '''
        fits_id = get_parameter(kwargs, "fits_id", -1)
        r = self.db.select_one(
            "select * from ifs_result_0 where id=?", (fits_id,))
        return r

    def read(self, **kwargs):
        ''' yield bytes of fits file

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
                "select * from ifs_result_0 where id=?", (fits_id))
            if r is not None:
                file_path = r["file_path"]

        if file_path is not None:
            chunk_size = get_parameter(kwargs, "chunk_size", 20480)
            return yield_file_bytes(os.path.join(self.root_dir, file_path), chunk_size)

    def write(self, **kwargs):
        ''' copy a local level 0 file to file storage, and insert a record into database

        parameter kwargs:
            raw_id = [int],
            file_path = [str],
            proc_type = [str]
        '''
        raw_id = get_parameter(kwargs, "raw_id")
        file_path = get_parameter(kwargs, "file_path")
        proc_type = get_parameter(kwargs, "proc_type", "default")

        if file_path is None:
            raise Exception("file_path need to be defined")

        new_file_dir = create_dir(os.path.join(self.root_dir, "results0"),
                self.sub_system, 
                "/".join([str(datetime.datetime.now().year),"%02d"%(datetime.datetime.now().month),"%02d"%(datetime.datetime.now().day)]))
        

        file_basename = os.path.basename(file_path)
        new_file_path = os.path.join(new_file_dir, file_basename)
        shutil.copyfile(file_path, new_file_path)

        self.db.execute(
            'INSERT INTO ifs_result_0 (filename, file_path, raw_id,  proc_type, create_time) \
                VALUES(?,?,?,?,?)',
            (file_basename, new_file_path.replace(self.root_dir, '')[1:], raw_id, proc_type, format_time_ms(time.time()))
        )

        self.db.end()

        log.info("result0 fits %s imported.", file_path)
        return new_file_path