import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.msc import Level1PrcRecord
from csst_dfs_commons.models.common import from_dict_list

log = logging.getLogger('csst')

class Level1PrcApi(object):
    def __init__(self, sub_system = "msc"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()

    def find(self, **kwargs):
        ''' retrieve level1 procedure records from database

        parameter kwargs:
            level1_id: [int]
            pipeline_id: [str]
            prc_module: [str]
            prc_status : [int]

        return: csst_dfs_common.models.Result
        '''
        try:
            level1_id = get_parameter(kwargs, "level1_id", 0)
            pipeline_id = get_parameter(kwargs, "pipeline_id")
            prc_module = get_parameter(kwargs, "prc_module")
            prc_status = get_parameter(kwargs, "prc_status")

            sql_data = f"select * from msc_level1_prc"

            sql_condition = f"where level1_id={level1_id}"
            if pipeline_id:
                sql_condition = sql_condition + " and pipeline_id='" + pipeline_id + "'"
            if prc_module:
                sql_condition = sql_condition + " and prc_module ='" + prc_module + "'"
            if prc_status:
                sql_condition = f"{sql_condition} and prc_status={prc_status}"   

            sql_data = f"{sql_data} {sql_condition}"

            _, records = self.db.select_many(sql_data)
            return Result.ok_data(data=from_dict_list(Level1PrcRecord, records)).append("totalCount", len(records))

        except Exception as e:
            return Result.error(message=str(e))

    def update_proc_status(self, **kwargs):
        ''' update the status of reduction

        parameter kwargs:
            id : [int],
            status : [int]

        return csst_dfs_common.models.Result
        '''
        id = get_parameter(kwargs, "id")
        status = get_parameter(kwargs, "status")

        try:
            existed = self.db.exists(
                "select * from msc_level1_prc where id=?",
                (id,)
            )
            if not existed:
                log.warning('%s not found' %(id, ))
                return Result.error(message ='%s not found' %(id, ))
            self.db.execute(
                'update msc_level1_prc set prc_status=?, prc_time=? where id=?',
                (status, format_time_ms(time.time()), id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def write(self, **kwargs):
        ''' insert a level1 procedure record into database
 
        parameter kwargs:
            level1_id : [int]
            pipeline_id : [str]
            prc_module : [str]
            params_file_path : [str]
            prc_status : [int]
            prc_time : [str]
            result_file_path : [str]
        return csst_dfs_common.models.Result
        '''   

        rec = Level1PrcRecord(
            id = 0,
            level1_id = get_parameter(kwargs, "level1_id", 0),
            pipeline_id = get_parameter(kwargs, "pipeline_id"),
            prc_module = get_parameter(kwargs, "prc_module"),
            params_file_path = get_parameter(kwargs, "params_file_path"),
            prc_status = get_parameter(kwargs, "prc_status", -1),
            prc_time = get_parameter(kwargs, "prc_time"),
            result_file_path = get_parameter(kwargs, "result_file_path")
        )
        try:
            self.db.execute(
                'INSERT INTO msc_level1_prc (level1_id,pipeline_id,prc_module, params_file_path, prc_status,prc_time,result_file_path) \
                    VALUES(?,?,?,?,?,?,?)',
                (rec.level1_id, rec.pipeline_id, rec.prc_module, rec.params_file_path, rec.prc_status, rec.prc_time, rec.result_file_path)
            )
            self.db.end()
            rec.id = self.db.last_row_id()

            return Result.ok_data(data=rec)

        except Exception as e:
            log.error(e)
            return Result.error(message=str(e)) 

