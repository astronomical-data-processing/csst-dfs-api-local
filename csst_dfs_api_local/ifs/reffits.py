import logging
import os
import time, datetime
import shutil
from astropy.io import fits

from ..common.db import DBClient
from ..common.utils import *

log = logging.getLogger('csst')
class RefFitsApi(object):
    REF_FITS_BIAS = "bias"
    REF_FITS_FLAT = "flat"
    REF_FITS_DARK = "dark"
    REF_FITS_SKY = "sky"
    REF_FITS_ARC = "arc"

    REF_FITS_TYPES = [REF_FITS_BIAS, REF_FITS_FLAT, REF_FITS_DARK, REF_FITS_SKY, REF_FITS_ARC]

    def __init__(self, sub_system = "ifs"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.check_dir()
        self.db = DBClient()

    def check_dir(self):
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)
            log.info("using [%s] as root directory", self.root_dir)
        if not os.path.exists(os.path.join(self.root_dir, "refs")):
            os.mkdir(os.path.join(self.root_dir, "refs"))

    def find(self, **kwargs):
        '''
        parameter kwargs:
            obs_time = [int],
            file_name = [str],
            ccd_num = [int],
            exp_time = (start, end),
            status = [int],
            ref_type = [str]

        return list of reference's files records
        '''
        obs_time = get_parameter(kwargs, "obs_time")
        file_name = get_parameter(kwargs, "file_name")
        exp_time = get_parameter(kwargs, "exp_time", (None, format_time_ms(time.time())))
        ccd_num = get_parameter(kwargs, "ccd_num")
        status = get_parameter(kwargs, "status")
        ref_type = get_parameter(kwargs, "ref_type")
        
        sql = []

        sql.append("select * from ifs_ref_fits where exp_time<='" + exp_time[1] + "'")

        if exp_time[0] is not None:
            sql.append(" and exp_time>='" + exp_time[0] + "'")
        if obs_time is not None:
            sql.append(" and obs_time=" + obs_time)
        if ccd_num is not None:
            sql.append(" and ccd_num=" + ccd_num)
        if ref_type is not None:
            sql.append(" and ref_type='" + ref_type + "'")           
        if status is not None:
            sql.append(" and status=" + status)

        if file_name:
            sql = ["select * from ifs_ref_fits where filename='" + file_name + "'"]
        sql.append(" order by exp_time desc")
        _, r = self.db.select_many("".join(sql))

        return r

    def get(self, **kwargs):
        '''query database, return a record as dict

        parameter kwargs:
            fits_id = [int] 

        return dict or None
        '''
        fits_id = get_parameter(kwargs, "fits_id", -1)
        r = self.db.select_one(
            "select * from ifs_ref_fits where id=?", (fits_id,))
        return r

    def read(self, **kwargs):
        '''
        parameter kwargs:
            fits_id = [int],
            file_path = [str], 
            chunk_size = [int]

        yield bytes of fits file
        '''
        fits_id = get_parameter(kwargs, "fits_id")
        file_path = get_parameter(kwargs, "file_path")

        if fits_id is None and file_path is None:
            raise Exception("fits_id or file_path need to be defined")

        if fits_id is not None:
            r = self.db.select_one(
                "select * from ifs_ref_fits where id=?", (fits_id))
            if r is not None:
                file_path = r["file_path"]

        if file_path is not None:
            chunk_size = get_parameter(kwargs, "chunk_size", 20480)
            return yield_file_bytes(os.path.join(self.root_dir, file_path), chunk_size)

    def update_status(self, **kwargs):
        '''
        parameter kwargs:
            fits_id = [int],
            status = [int]
        '''

        fits_id = get_parameter(kwargs, "fits_id")
        status = get_parameter(kwargs, "status")

        existed = self.db.exists(
            "select * from ifs_ref_fits where id=?",
            (fits_id,)
        )
        if existed:
            log.warning('%s not found' %(fits_id, ))
            return
        self.db.execute(
            'update ifs_ref_fits set status=? where id=?',
            (status, fits_id)
        )  
        self.db.end() 

    def import2db(self, **kwargs):
        '''
        parameter kwargs:
            file_path = [str]
            ref_type = [str]

            insert into database
        '''
       
        file_path = get_parameter(kwargs, "file_path")

        if file_path is None:
            raise Exception("file_path need to be defined")
        
        file_full_path = os.path.join(self.root_dir, file_path)

        if not os.path.exists(file_full_path):
            raise Exception("%s not found"%(file_full_path))

        file_name = os.path.basename(file_path)

        existed = self.db.exists(
            "select * from ifs_ref_fits where filename=?",
            (file_name,)
        )
        if existed:
            log.warning('%s has already been imported' %(file_path, ))
            return

        hu = fits.getheader(file_full_path)
        obs_time = hu['obst'] if 'obst' in hu else ''
        ccd_num = hu['ccd_num'] if 'ccd_num' in hu else 0
        exp_time = format_time_ms(time.time())

        ref_type = get_parameter(kwargs, "ref_type")
        
        if ref_type is None:
            if 'flat' in file_name.lower():
                ref_type = 'flat'
            elif 'bias' in file_name.lower():
                ref_type = 'bias'
            elif 'hgar' in file_name.lower():
                ref_type = 'arc'
            elif 'sky' in file_name.lower():
                ref_type = 'sky'
            else:
                ref_type = ""

        
        self.db.execute(
            'INSERT INTO ifs_ref_fits (filename, obs_time, ccd_num, exp_time, file_path, ref_type, status, create_time) \
                VALUES(?,?,?,?,?,?,?,?)',
            (file_name, obs_time, ccd_num, exp_time, file_path, ref_type, 1, format_time_ms(time.time()))
        )

        self.db.end()

        log.info("ref fits %s imported.", file_path)

    def write(self, **kwargs):
        ''' copy a local file to file storage, then reduce the header of fits file and insert a record into database
 
        parameter kwargs:
            file_path = [str]
        '''            
        file_path = get_parameter(kwargs, "file_path")

        new_file_dir = create_dir(os.path.join(self.root_dir, "refs"),
                self.sub_system, 
                "/".join([str(datetime.now().year),"%02d"%(datetime.now().month),"%02d"%(datetime.now().day)]))
        

        file_basename = os.path.basename(file_path)
        new_file_path = os.path.join(new_file_dir, file_basename)
        shutil.copyfile(file_path, new_file_path)

        file_path = new_file_path.replace(self.root_dir, '')
        if file_path.index("/") == 0:
            file_path = file_path[1:]

        self.import2db(file_path = file_path)
        

    def associate_raw(self, **kwargs):
        ''' associate raw fits to reference file
        parameter kwargs:
            raw_fits_ids = [list]
            ref_fits_id = [int]
        '''        
        raw_fits_ids = get_parameter(kwargs, "raw_fits_ids")
        ref_fits_id = get_parameter(kwargs, "ref_fits_id")

        if raw_fits_ids is None or ref_fits_id is None:
            raise Exception("raw_fits_ids or ref_fits_id is None")

        sql = 'INSERT INTO ifs_raw_ref (fit_id, ref_id, create_time) values '
        values = ["(%s,%s,'%s')"%(i,ref_fits_id,format_time_ms(time.time())) for i in raw_fits_ids]

        self.db.execute(sql + ",".join(values))

        self.db.end()

        log.info("%s associate to %s imported.", raw_fits_ids, ref_fits_id)



