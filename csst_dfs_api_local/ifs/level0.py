import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.ifs import Level0Record
from csst_dfs_commons.models.common import from_dict_list
from .ingest import ingest_one

log = logging.getLogger('csst')

class Level0DataApi(object):
    def __init__(self, sub_system = "ifs"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()

    def find(self, **kwargs):
        ''' retrieve level0 records from database

        parameter kwargs:
            obs_id: [str],
            detector_no: [str],
            obs_type: [str],
            object_name: [str],
            obs_time : (start, end),
            qc0_status : [int],
            prc_status : [int],
            file_name: [str],
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            obs_id = get_parameter(kwargs, "obs_id")
            detector_no = get_parameter(kwargs, "detector_no")
            obs_type = get_parameter(kwargs, "obs_type")
            object_name = get_parameter(kwargs, "object_name")
            version = get_parameter(kwargs, "version")
            exp_time_start = get_parameter(kwargs, "obs_time", [None, None])[0]
            exp_time_end = get_parameter(kwargs, "obs_time", [None, None])[1]
            qc0_status = get_parameter(kwargs, "qc0_status")
            prc_status = get_parameter(kwargs, "prc_status")
            file_name = get_parameter(kwargs, "file_name")
            limit = get_parameter(kwargs, "limit", 0)
            ra = get_parameter(kwargs, "ra", None)
            dec = get_parameter(kwargs, "limit", None)
            radius = get_parameter(kwargs, "limit", 0)

            sql_count = 'select count(*) as c from ifs_level0_data d left join ifs_level0_header h on d.id=h.id where 1=1'
            sql_data = 'select d.* from ifs_level0_data d left join ifs_level0_header h on d.id=h.id where 1=1'

            sql_condition = "" 
            if obs_id:
                sql_condition = f"{sql_condition} and d.obs_id='{obs_id}'"              
            if detector_no:
                sql_condition = f"{sql_condition} and d.detector_no='{detector_no}'"
            if obs_type:
                sql_condition = f"{sql_condition} and d.obs_type='{obs_type}'"
            if exp_time_start:
                sql_condition = f"{sql_condition} and d.obs_time >='{exp_time_start}'"
            if exp_time_end:
                sql_condition = f"{sql_condition} and d.obs_time <='{exp_time_end}'"
            if qc0_status:
                sql_condition = f"{sql_condition} and d.qc0_status={qc0_status}"
            if prc_status:
                sql_condition = f"{sql_condition} and d.prc_status={prc_status}"  
            if object_name:
                sql_condition = f"{sql_condition} and h.object_name='{object_name}'"
            if version:
                sql_condition = f"{sql_condition} and h.version='{version}'"  
            if ra:
                sql_condition = f"{sql_condition} and (h.ra <= {ra+radius} and h.ra >={ra-radius})"  
            if dec:
                sql_condition = f"{sql_condition} and (h.dec <= {dec+radius} and h.ra >={dec-radius})"

            if file_name:
                sql_condition = f" and d.filename='{file_name}'"  

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
            id : [int],
            level0_id : [str]

        return csst_dfs_common.models.Result
        '''
        id = get_parameter(kwargs, "id", 0)
        level0_id = get_parameter(kwargs, "level0_id", "")

        if id == 0 and level0_id == "":
            return Result.error(message="at least define id or level0_id") 

        if id != 0: 
            return self.get_by_id(id)
        if level0_id != "": 
            return self.get_by_level0_id(level0_id)

    def get_by_id(self, id: int):
        try:
            r = self.db.select_one(
                "select * from ifs_level0_data where id=?", (id,))
            if r:
                return Result.ok_data(data=Level0Record().from_dict(r))
            else:
                return Result.error(message=f"id:{id} not found")  
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))  

    def get_by_level0_id(self, level0_id: str):
        try:
            r = self.db.select_one(
                "select * from ifs_level0_data where level0_id=?", (level0_id,))
            if r:
                return Result.ok_data(data=Level0Record().from_dict(r))
            else:
                return Result.error(message=f"level0_id:{level0_id} not found")  
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))  

    def update_proc_status(self, **kwargs):
        ''' update the status of reduction

        parameter kwargs:
            id : [int],
            level0_id : [str],
            status : [int]

        return csst_dfs_common.models.Result
        '''
        id = get_parameter(kwargs, "id")
        level0_id = get_parameter(kwargs, "level0_id")
        result = self.get(id = id, level0_id = level0_id)

        if not result.success:
            return Result.error(message="not found")

        id = result.data.id
        status = get_parameter(kwargs, "status")
        try:
            self.db.execute(
                'update ifs_level0_data set prc_status=?, prc_time=? where id=?',
                (status, format_time_ms(time.time()), id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def update_qc0_status(self, **kwargs):
        ''' update the status of QC0
        
        parameter kwargs:
            id : [int],
            level0_id : [str],
            status : [int]
        '''        
        id = get_parameter(kwargs, "id")
        level0_id = get_parameter(kwargs, "level0_id")
        result = self.get(id = id, level0_id = level0_id)

        if not result.success:
            return Result.error(message="not found")

        id = result.data.id
        status = get_parameter(kwargs, "status")
        try:
            self.db.execute(
                'update ifs_level0_data set qc0_status=?, qc0_time=? where id=?',
                (status, format_time_ms(time.time()), id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def write(self, **kwargs):
        ''' insert a level0 data record into database
 
        parameter kwargs:
            file_path = [str],
            copyfiles = [boolean]
        return: csst_dfs_common.models.Result
        '''          

        file_path = get_parameter(kwargs, "file_path")
        copyfiles = get_parameter(kwargs, "copyfiles", False)
        try:
            rec = ingest_one(file_path, self.db, copyfiles)
            return Result.ok_data(data=rec)
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e)) 


