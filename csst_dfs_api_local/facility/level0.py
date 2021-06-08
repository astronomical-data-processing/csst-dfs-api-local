import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.facility import Level0Record
from csst_dfs_commons.models.common import from_dict_list

log = logging.getLogger('csst')

class Level0DataApi(object):
    def __init__(self):
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()

    def find(self, **kwargs):
        ''' retrieve level0 records from database

        parameter kwargs:
            obs_id: [int]
            detector_no: [str]
            obs_type: [str]
            obs_time : (start, end),
            qc0_status : [int],
            prc_status : [int],
            file_name: [str]
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            obs_id = get_parameter(kwargs, "obs_id")
            detector_no = get_parameter(kwargs, "detector_no")
            obs_type = get_parameter(kwargs, "obs_type")
            exp_time_start = get_parameter(kwargs, "obs_time", [None, None])[0]
            exp_time_end = get_parameter(kwargs, "obs_time", [None, None])[1]
            qc0_status = get_parameter(kwargs, "qc0_status")
            prc_status = get_parameter(kwargs, "prc_status")
            file_name = get_parameter(kwargs, "file_name")
            limit = get_parameter(kwargs, "limit", 0)

            sql_count = "select count(*) as c from t_level0_data where 1=1"
            sql_data = f"select * from t_level0_data where 1=1"

            sql_condition = "" 
            if obs_id > 0:
                sql_condition = f"{sql_condition} and obs_id={obs_id}"              
            if detector_no:
                sql_condition = f"{sql_condition} and detector_no='{detector_no}'"
            if obs_type:
                sql_condition = f"{sql_condition} and obs_type='{obs_type}'"
            if exp_time_start:
                sql_condition = f"{sql_condition} and obs_time >='{exp_time_start}'"
            if exp_time_end:
                sql_condition = f"{sql_condition} and obs_time <='{exp_time_end}'"
            if qc0_status:
                sql_condition = f"{sql_condition} and qc0_status={qc0_status}"
            if prc_status:
                sql_condition = f"{sql_condition} and prc_status={prc_status}"   
            if file_name:
                sql_condition = f" and filename='{file_name}'"  

            sql_count = f"{sql_count} {sql_condition}"
            sql_data = f"{sql_data} {sql_condition}"

            if limit > 0:
                sql_data = f"{sql_data} limit {limit}"   

            totalCount = self.db.select_one(sql_count)
            _, records = self.db.select_many(sql_data)

            return Result.ok_data(data=from_dict_list(Level0Record, records)).append("totalCount", totalCount['c'])

        except Exception as e:
            return Result.error(message=str(e))

    def get(self, **kwargs):
        '''  fetch a record from database

        parameter kwargs:
            fits_id : [int] 

        return csst_dfs_common.models.Result
        '''
        try:
            fits_id = get_parameter(kwargs, "fits_id", -1)
            r = self.db.select_one(
                "select * from t_level0_data where id=?", (fits_id,))
            if r:
                return Result.ok_data(data=Level0Record().from_dict(r))
            else:
                return Result.error(message=f"fits_id:{fits_id} not found")  
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))   

    def update_proc_status(self, **kwargs):
        ''' update the status of reduction

        parameter kwargs:
            fits_id : [int],
            status : [int]

        return csst_dfs_common.models.Result
        '''
        fits_id = get_parameter(kwargs, "fits_id")
        status = get_parameter(kwargs, "status")
        try:
            existed = self.db.exists(
                "select * from t_level0_data where id=?",
                (fits_id,)
            )
            if not existed:
                log.warning('%s not found' %(fits_id, ))
                return Result.error(message ='%s not found' %(fits_id, ))
            self.db.execute(
                'update t_level0_data set prc_status=?, prc_time=? where id=?',
                (status, format_time_ms(time.time()), fits_id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def update_qc0_status(self, **kwargs):
        ''' update the status of QC0
        
        parameter kwargs:
            fits_id : [int],
            status : [int]
        '''        
        fits_id = get_parameter(kwargs, "fits_id")
        status = get_parameter(kwargs, "status")
        try:
            existed = self.db.exists(
                "select * from t_level0_data where id=?",
                (fits_id,)
            )
            if not existed:
                log.warning('%s not found' %(fits_id, ))
                return Result.error(message ='%s not found' %(fits_id, ))
            self.db.execute(
                'update t_level0_data set qc0_status=?, qc0_time=? where id=?',
                (status, format_time_ms(time.time()), fits_id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def write(self, **kwargs):
        ''' insert a level0 data record into database
 
        parameter kwargs:
            obs_id = [int]
            detector_no = [str]
            obs_type = [str]        
            obs_time = [str]
            exp_time = [int]
            detector_status_id = [int]
            filename = [str]
            file_path = [str]
        return: csst_dfs_common.models.Result
        '''          
        rec = Level0Record(
            obs_id = get_parameter(kwargs, "obs_id"),
            detector_no = get_parameter(kwargs, "detector_no"),
            obs_type = get_parameter(kwargs, "obs_type"),
            obs_time = get_parameter(kwargs, "obs_time"),
            exp_time = get_parameter(kwargs, "exp_time"),
            detector_status_id = get_parameter(kwargs, "detector_status_id"),
            filename = get_parameter(kwargs, "filename"),
            file_path = get_parameter(kwargs, "file_path")
        )
        try:
            existed = self.db.exists(
                    "select * from t_level0_data where filename=?",
                    (rec.filename,)
                )
            if existed:
                log.warning('%s existed' %(rec.filename, ))
                return Result.error(message ='%s existed' %(rec.filename, ))

            self.db.execute(
                'INSERT INTO t_level0_data (obs_id, detector_no, obs_type, obs_time, exp_time,detector_status_id, filename, file_path,qc0_status, prc_status,create_time) \
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                (rec.obs_id, rec.detector_no, rec.obs_type, rec.obs_time, rec.exp_time, rec.detector_status_id, rec.filename, rec.file_path,0,0,format_time_ms(time.time()))
            )
            self.db.end()
            rec.id = self.db.last_row_id()

            return Result.ok_data(data=rec)

        except Exception as e:
            log.error(e)
            return Result.error(message=str(e)) 


