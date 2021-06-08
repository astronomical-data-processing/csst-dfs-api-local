import os
import logging
import time, datetime
import shutil

from csst_dfs_commons.models import Result
from csst_dfs_commons.models.facility import Detector, DetectorStatus
from csst_dfs_commons.models.common import from_dict_list

from ..common.db import DBClient
from ..common.utils import *

log = logging.getLogger('csst')

class DetectorApi(object):
    def __init__(self):
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()

    def find(self, **kwargs):
        ''' retrieve detector records from database

        parameter kwargs:
            module_id: [str]
            key: [str]

        return: csst_dfs_common.models.Result
        '''
        try:
            module_id = get_parameter(kwargs, "module_id")
            key = get_parameter(kwargs, "key","")
            sql_data = f"select * from t_detector where 1=1"

            sql_condition = "" 
            if module_id:
                sql_condition = f"{sql_condition} and module_id='{module_id}'"

            sql_condition = f"{sql_condition} and (`no` like ? or detector_name like ?)"
            
            sql_data = f"{sql_data} {sql_condition}"
            _, records = self.db.select_many(sql_data,(f'%{key}%',f'%{key}%'))

            return Result.ok_data(data=from_dict_list(Detector, records)).append("totalCount", len(records))

        except Exception as e:
            return Result.error(message=str(e))

    def get(self, **kwargs):
        '''  fetch a record from database

        parameter kwargs:
            no : [str] 

        return csst_dfs_common.models.Result
        '''
        try:
            no = get_parameter(kwargs, "no")
            r = self.db.select_one(
                "select * from t_detector where no=?", (no,))
            if r:
                return Result.ok_data(data=Detector().from_dict(r))
            else:
                return Result.error(message=f"detector no:{no} not found")  
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))     

    def update(self, **kwargs):
        ''' update a detector by no

        parameter kwargs:
            no : [str],
            detector_name : [str],
            module_id : [str],
            filter_id : [str]

        return csst_dfs_common.models.Result
        '''
        try:
            no = get_parameter(kwargs, "no")
            result_get = self.get(no=no)
            if not result_get.success:
                return result_get

            detector_name = get_parameter(kwargs, "detector_name", result_get.data.detector_name),
            module_id = get_parameter(kwargs, "module_id", result_get.data.module_id),
            filter_id = get_parameter(kwargs, "filter_id", result_get.data.filter_id)

            sql_data = f"update t_detector set detector_name='{detector_name}',\
                    module_id='{module_id}',\
                    filter_id='{filter_id}',\
                    update_time=now() where `no`='{no}'"

            _ = self.db.execute(sql_data)
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def delete(self, **kwargs):
        ''' delete a detector by no

        parameter kwargs:
            no : [str]

        return csst_dfs_common.models.Result
        '''
        try:
            no = get_parameter(kwargs, "no")

            sql_data = f"delete from t_detector where `no`='{no}'"

            _ = self.db.execute(sql_data)
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def write(self, **kwargs):
        ''' insert a detector record into database
 
        parameter kwargs:
            no : [str],
            detector_name : [str],
            module_id : [str],
            filter_id : [str]
        return csst_dfs_common.models.Result
        '''   

        rec = Detector(
            no = get_parameter(kwargs, "no"),
            detector_name = get_parameter(kwargs, "detector_name"),
            module_id = get_parameter(kwargs, "module_id"),
            filter_id = get_parameter(kwargs, "filter_id"),
            create_time = format_time_ms(time.time())
        )
        try:
            existed = self.db.exists(
                    "select * from t_detector where no=?",
                    (rec.no,)
                )
            if existed:
                log.warning('%s existed' %(rec.no, ))
                return Result.error(message ='%s existed' %(rec.no, ))

            self.db.execute(
                'INSERT INTO t_detector (`no`,detector_name,module_id,filter_id,create_time) \
                    VALUES(?,?,?,?,?)',
                (rec.no, rec.detector_name, rec.module_id, rec.filter_id,rec.create_time)
            )
            self.db.end()
            return Result.ok_data(data=rec)
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def find_status(self, **kwargs):
        ''' retrieve a detector status's from database

        parameter kwargs:
            detector_no: [str]
            status_occur_time: (begin,end)
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            detector_no = get_parameter(kwargs, "detector_no")
            status_begin_time = get_parameter(kwargs, "status_occur_time", [None, None])[0]
            status_end_time = get_parameter(kwargs, "status_occur_time", [None, None])[1]              
            limit = get_parameter(kwargs, "limit", 0)

            sql_count = f"select count(*) as c from t_detector_status where detector_no='{detector_no}'"
            sql_data = f"select * from t_detector_status where detector_no='{detector_no}'"

            sql_condition = "" 
            if status_begin_time:
                sql_condition = f"{sql_condition} and status_time >='{status_begin_time}'"
            if status_end_time:
                sql_condition = f"{sql_condition} and status_time <='{status_end_time}'"
              
            sql_count = f"{sql_count} {sql_condition}"
            sql_data = f"{sql_data} {sql_condition}"

            if limit > 0:
                sql_data = f"{sql_data} limit {limit}"   

            totalCount = self.mysql_client.select_one(sql_count)
            _, records = self.mysql_client.select_many(sql_data)

            return Result.ok_data(data=from_dict_list(DetectorStatus, records)).append("totalCount", totalCount['c'])

        except Exception as e:
            return Result.error(message=str(e))

    def get_status(self, **kwargs):
        '''  fetch a record from database

        parameter kwargs:
            id : [int] 

        return csst_dfs_common.models.Result
        '''
        try:
            id = get_parameter(kwargs, "id", -1)
            r = self.db.select_one(
                "select * from t_detector_status where id=?", (id,))
            if r:
                return Result.ok_data(data=DetectorStatus().from_dict(r))
            else:
                return Result.error(message=f"id:{id} not found")  
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))    
    
    def write_status(self, **kwargs):
        ''' insert a detector status into database
 
        parameter kwargs:
            detector_no : [str],
            status : [str],
            status_time : [str]
        return csst_dfs_common.models.Result
        '''   

        rec = DetectorStatus(
            id = 0,
            detector_no = get_parameter(kwargs, "detector_no"),
            status = get_parameter(kwargs, "status"),
            status_time = get_parameter(kwargs, "status_time")
        )
        try:
            self.db.execute(
                'INSERT INTO t_detector_status (detector_no,status,status_time,create_time) \
                    VALUES(?,?,?,?)',
                (rec.detector_no, rec.status, rec.status_time,format_time_ms(time.time()))
            )
            self.db.end()
            rec.id = self.db.last_row_id()

            return Result.ok_data(data=rec)

        except Exception as e:
            log.error(e)
            return Result.error(message=str(e)) 