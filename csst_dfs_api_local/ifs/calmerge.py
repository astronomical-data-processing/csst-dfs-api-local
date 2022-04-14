import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.ifs import CalMergeRecord
from csst_dfs_commons.models.common import from_dict_list
from .level0 import Level0DataApi

log = logging.getLogger('csst')

class CalMergeApi(object):
    def __init__(self, sub_system = "ifs"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()
        self.level0Api = Level0DataApi()

    def get_latest_by_l0(self, **kwargs):
        ''' retrieve calibration merge records from database by level0 data
        
        :param kwargs: Parameter dictionary, key items support:
            level0_id: [str],
            ref_type: [str]

        :returns: csst_dfs_common.models.Result
        '''
        try:
            level0_id = get_parameter(kwargs, "level0_id")
            ref_type = get_parameter(kwargs, "ref_type")

            level0_data = self.level0Api.get_by_level0_id(level0_id)
            if level0_data is None:
                return Result.error(message = "level0 data [%s]not found"%(level0_id))
            
            sql_data = f"select * from ifs_cal_merge where detector_no='{level0_data.data.detector_no}' and ref_type='{ref_type}' and obs_time >= '{level0_data.data.obs_time}' order by obs_time ASC limit 1"

            r = self.db.select_one(sql_data)
            if r:
                rec = CalMergeRecord().from_dict(r)
                return Result.ok_data(data=rec)
            
            sql_data = f"select * from ifs_cal_merge where detector_no='{level0_data.data.detector_no}' and ref_type='{ref_type}' and obs_time <= '{level0_data.data.obs_time}' order by obs_time DESC limit 1"

            r = self.db.select_one(sql_data)
            if r:
                rec = CalMergeRecord().from_dict(r)
                return Result.ok_data(data=rec)            

            return Result.error(message = "not found")

        except Exception as e:
            return Result.error(message=str(e))

    def find(self, **kwargs):
        ''' retrieve calibration merge records from database

        parameter kwargs:
            detector_no: [str]
            ref_type: [str]
            obs_time: (start,end)
            qc1_status : [int]
            prc_status : [int]
            file_name: [str]
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            detector_no = get_parameter(kwargs, "detector_no")
            ref_type = get_parameter(kwargs, "ref_type")
            exp_time_start = get_parameter(kwargs, "obs_time", [None, None])[0]
            exp_time_end = get_parameter(kwargs, "obs_time", [None, None])[1]              
            qc1_status = get_parameter(kwargs, "qc1_status")
            prc_status = get_parameter(kwargs, "prc_status")
            file_name = get_parameter(kwargs, "file_name")
            limit = get_parameter(kwargs, "limit", 0)

            sql_count = "select count(*) as c from ifs_cal_merge where 1=1"
            sql_data = f"select * from ifs_cal_merge where 1=1"

            sql_condition = "" 
            if detector_no:
                sql_condition = f"{sql_condition} and detector_no='{detector_no}'"
            if ref_type:
                sql_condition = f"{sql_condition} and ref_type='{ref_type}'"
            if exp_time_start:
                sql_condition = f"{sql_condition} and obs_time >='{exp_time_start}'"
            if exp_time_end:
                sql_condition = f"{sql_condition} and obs_time <='{exp_time_end}'"
            if qc1_status:
                sql_condition = f"{sql_condition} and qc1_status={qc1_status}"
            if prc_status:
                sql_condition = f"{sql_condition} and prc_status={prc_status}"   

            if file_name:
                sql_condition = f" and filename={file_name}"  

            sql_count = f"{sql_count} {sql_condition}"
            sql_data = f"{sql_data} {sql_condition}"

            log.info(sql_count)
            log.info(sql_data)

            if limit > 0:
                sql_data = f"{sql_data} limit {limit}"   

            totalCount = self.db.select_one(sql_count)
            _, records = self.db.select_many(sql_data)

            return Result.ok_data(data=from_dict_list(CalMergeRecord, records)).append("totalCount", totalCount['c'])

        except Exception as e:
            return Result.error(message=str(e))

    def get(self, **kwargs):
        '''  fetch a record from database

        parameter kwargs:
            id : [int],
            cal_id : [str]

        return csst_dfs_common.models.Result
        '''
        id = get_parameter(kwargs, "id", 0)
        cal_id = get_parameter(kwargs, "cal_id", "")

        if id == 0 and cal_id == "":
            return Result.error(message="at least define id or cal_id") 

        if id != 0: 
            return self.get_by_id(id)
        if cal_id != "": 
            return self.get_by_cal_id(cal_id)

    def get_by_id(self, iid: int):
        try:
            r = self.db.select_one(
                "select * from ifs_cal_merge where id=?", (iid,))
            if r:

                sql_get_level0_id = f"select level0_id from ifs_cal2level0 where merge_id={r['id']}" 
                _, records = self.db.select_many(sql_get_level0_id)
                level0_ids = [r["level0_id"] for r in records]

                rec = CalMergeRecord().from_dict(r)
                rec.level0_ids = level0_ids
                return Result.ok_data(data=rec)
            else:
                return Result.error(message=f"id:{iid} not found")
                    
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def get_by_cal_id(self, cal_id: str):
        try:
            r = self.db.select_one(
                "select * from ifs_cal_merge where cal_id=?", (cal_id,))
            if r:

                sql_get_level0_id = f"select level0_id from ifs_cal2level0 where merge_id={r['id']}" 
                _, records = self.db.select_many(sql_get_level0_id)
                level0_ids = [r["level0_id"] for r in records]

                rec = CalMergeRecord().from_dict(r)
                rec.level0_ids = level0_ids
                return Result.ok_data(data=rec)
            else:
                return Result.error(message=f"id:{id} not found")
                    
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def update_qc1_status(self, **kwargs):
        ''' update the status of reduction

        parameter kwargs:
            id : [int],
            cal_id : [str],
            status : [int]

        return csst_dfs_common.models.Result
        '''
        id = get_parameter(kwargs, "id", 0)
        cal_id = get_parameter(kwargs, "cal_id", "")
        result = self.get(id = id, cal_id = cal_id)

        if not result.success:
            return Result.error(message="not found")

        id = result.data.id
        status = get_parameter(kwargs, "status")

        try:
            self.db.execute(
                'update ifs_cal_merge set qc1_status=?, qc1_time=? where id=?',
                (status, format_time_ms(time.time()), id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def update_proc_status(self, **kwargs):
        ''' update the status of reduction

        parameter kwargs:
            id : [int],
            cal_id : [str],
            status : [int]

        return csst_dfs_common.models.Result
        '''
        id = get_parameter(kwargs, "id", 0)
        cal_id = get_parameter(kwargs, "cal_id", "")
        result = self.get(id = id, cal_id = cal_id)

        if not result.success:
            return Result.error(message="not found")

        id = result.data.id
        status = get_parameter(kwargs, "status")

        try:
            existed = self.db.exists(
                "select * from ifs_cal_merge where id=?",
                (id,)
            )
            if not existed:
                log.warning('%s not found' %(id, ))
                return Result.error(message ='%s not found' %(id, ))
            self.db.execute(
                'update ifs_cal_merge set prc_status=?, prc_time=? where id=?',
                (status, format_time_ms(time.time()), id)
            )
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def write(self, **kwargs):
        ''' insert a calibration merge record into database
 
        parameter kwargs:
            cal_id : [str]
            detector_no : [str]
            ref_type : [str]
            obs_time : [str]
            exp_time : [float]
            prc_status : [int]
            prc_time : [str]
            filename : [str]
            file_path : [str]
            level0_ids : [list]
        return csst_dfs_common.models.Result
        '''   

        rec = CalMergeRecord(
            id = 0,
            cal_id =  get_parameter(kwargs, "cal_id"),
            detector_no = get_parameter(kwargs, "detector_no"),
            ref_type = get_parameter(kwargs, "ref_type"),
            obs_time = get_parameter(kwargs, "obs_time"),
            exp_time = get_parameter(kwargs, "exp_time"),
            filename = get_parameter(kwargs, "filename"),
            file_path = get_parameter(kwargs, "file_path"),
            prc_status = get_parameter(kwargs, "prc_status", -1),
            prc_time = get_parameter(kwargs, "prc_time"),
            level0_ids = get_parameter(kwargs, "level0_ids", [])
        )
        try:
            self.db.execute(
                'INSERT INTO ifs_cal_merge (cal_id,detector_no,ref_type,obs_time,exp_time,filename,file_path,prc_status,prc_time,create_time) \
                    VALUES(?,?,?,?,?,?,?,?,?,?)',
                (rec.cal_id, rec.detector_no, rec.ref_type, rec.obs_time, rec.exp_time, rec.filename, rec.file_path,rec.prc_status,rec.prc_time,format_time_ms(time.time()))
            )
            self.db.end()
            rec.id = self.db.last_row_id()

            sql_level0_ids = "insert into ifs_cal2level0 (merge_id,level0_id) values "
            values = ["(%s,%s)"%(rec.id,i) for i in rec.level0_ids]
            _ = self.db.execute(sql_level0_ids + ",".join(values))            

            self.db.end()

            return Result.ok_data(data=rec)

        except Exception as e:
            log.error(e)
            return Result.error(message=str(e)) 