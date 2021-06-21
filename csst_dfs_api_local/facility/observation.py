import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.facility import Observation
from csst_dfs_commons.models.common import from_dict_list

log = logging.getLogger('csst')
class ObservationApi(object):
    def __init__(self):
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()
    
    def find(self, **kwargs):
        ''' retrieve exposure records from database

        parameter kwargs:
            module_id: [str]
            obs_type: [str]
            obs_time : (start, end),
            qc0_status : [int],
            prc_status : [int],
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            module_id = get_parameter(kwargs, "module_id")
            obs_type = get_parameter(kwargs, "obs_type")
            exp_time_start = get_parameter(kwargs, "obs_time", [None, None])[0]
            exp_time_end = get_parameter(kwargs, "obs_time", [None, None])[1]
            qc0_status = get_parameter(kwargs, "qc0_status")
            prc_status = get_parameter(kwargs, "prc_status")
            limit = get_parameter(kwargs, "limit", 0)
            sql_count = "select count(*) as c from t_observation"
            sql_data = f"select * from t_observation"

            sql_condition = "where module_id='" + module_id + "'" 
            if obs_type:
                sql_condition = sql_condition + " and obs_type='" + obs_type + "'"
            if exp_time_start:
                sql_condition = sql_condition + " and obs_time >='" + exp_time_start + "'"
            if exp_time_end:
                sql_condition = sql_condition + " and obs_time <='" + exp_time_end + "'"
            if qc0_status:
                sql_condition = f"{sql_condition} and qc0_status={qc0_status}"
            if prc_status:
                sql_condition = f"{sql_condition} and prc_status={prc_status}"   

            sql_count = f"{sql_count} {sql_condition}"
            sql_data = f"{sql_data} {sql_condition}"

            if limit > 0:
                sql_data = f"{sql_data} limit {limit}"   

            totalCount = self.db.select_one(sql_count)
            _, records = self.db.select_many(sql_data)

            return Result.ok_data(data=from_dict_list(Observation, records)).append("totalCount", totalCount['c'])

        except Exception as e:
            return Result.error(message=str(e))
        
    def get(self, **kwargs):
        '''
        parameter kwargs:
            obs_id = [int] 

        return dict or None
        '''
        try:
            obs_id = get_parameter(kwargs, "obs_id", -1)
            r = self.db.select_one(
                "select * from t_observation where id=?", (obs_id,))
            if r:
                return Result.ok_data(data=Observation().from_dict(r))
            else:
                return Result.error(message=f"obs_id:{obs_id} not found")  
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))        
    def update_proc_status(self, **kwargs):
        ''' update the status of reduction

        parameter kwargs:
            obs_id : [int],
            status : [int]

        return csst_dfs_common.models.Result
        '''
        obs_id = get_parameter(kwargs, "obs_id")
        status = get_parameter(kwargs, "status")
        try:
            existed = self.db.exists(
                "select * from t_observation where id=?",
                (obs_id,)
            )
            if not existed:
                log.warning('%s not found' %(obs_id, ))
                return Result.error(message ='%s not found' %(obs_id, ))
            self.db.execute(
                'update t_observation set prc_status=?, prc_time=? where id=?',
                (status, format_time_ms(time.time()), obs_id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def update_qc0_status(self, **kwargs):
        ''' update the status of QC0
        
        parameter kwargs:
            obs_id : [int],
            status : [int]
        '''        
        obs_id = get_parameter(kwargs, "obs_id")
        status = get_parameter(kwargs, "status")
        try:
            existed = self.db.exists(
                "select * from t_observation where id=?",
                (obs_id,)
            )
            if not existed:
                log.warning('%s not found' %(obs_id, ))
                return Result.error(message ='%s not found' %(obs_id, ))
            self.db.execute(
                'update t_observation set qc0_status=?, qc0_time=? where id=?',
                (status, format_time_ms(time.time()), obs_id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def write(self, **kwargs):
        ''' insert a observational record into database
 
        parameter kwargs:
            obs_id = [int]
            obs_time = [str]
            exp_time = [int]
            module_id = [str]
            obs_type = [str]
            facility_status_id = [int]
            module_status_id = [int]
        return: csst_dfs_common.models.Result
        '''   
        obs_id = get_parameter(kwargs, "obs_id", 0)
        obs_time = get_parameter(kwargs, "obs_time")
        exp_time = get_parameter(kwargs, "exp_time")
        module_id = get_parameter(kwargs, "module_id")
        obs_type = get_parameter(kwargs, "obs_type")
        facility_status_id = get_parameter(kwargs, "facility_status_id")
        module_status_id = get_parameter(kwargs, "module_status_id")

        try:
            if obs_id == 0:
                r = self.db.select_one("select max(id) as max_id from t_observation")
                max_id = 0 if r["max_id"] is None else r["max_id"]
                obs_id = max_id + 1

            existed = self.db.exists(
                "select * from t_observation where id=?",
                (obs_id,)
            )
            if existed:
                log.warning('%s existed' %(obs_id, ))
                return Result.error(message ='%s existed' %(obs_id, ))

            self.db.execute(
                'INSERT INTO t_observation (id,obs_time,exp_time,module_id,obs_type,facility_status_id, module_status_id, qc0_status,create_time) \
                    VALUES(?,?,?,?,?,?,?,?,?)',
                (obs_id, obs_time, exp_time, module_id, obs_type, facility_status_id, module_status_id,-1,format_time_ms(time.time()))
            )
            self.db.end()

            return self.get(obs_id = obs_id)

        except Exception as e:
            log.error(e)
            return Result.error(message=str(e)) 