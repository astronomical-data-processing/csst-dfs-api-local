import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.msc import Level1Record
from csst_dfs_commons.models.common import from_dict_list

log = logging.getLogger('csst')

class Level1DataApi(object):
    def __init__(self, sub_system = "msc"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()

    def find(self, **kwargs):
        ''' retrieve level1 records from database

        parameter kwargs:
            raw_id: [int]
            data_type: [str]
            obs_type: [str]
            create_time : (start, end),
            qc1_status : [int],
            prc_status : [int],
            filename: [str]
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            raw_id = get_parameter(kwargs, "raw_id")
            data_type = get_parameter(kwargs, "data_type")
            create_time_start = get_parameter(kwargs, "create_time", [None, None])[0]
            create_time_end = get_parameter(kwargs, "create_time", [None, None])[1]
            qc1_status = get_parameter(kwargs, "qc1_status")
            prc_status = get_parameter(kwargs, "prc_status")
            filename = get_parameter(kwargs, "filename")
            limit = get_parameter(kwargs, "limit", 0)

            sql_count = "select count(*) as c from msc_level1_data where 1=1"
            sql_data = f"select * from msc_level1_data where 1=1"

            sql_condition = "" 
            if raw_id:
                sql_condition = f"{sql_condition} and raw_id={raw_id}"
            if data_type:
                sql_condition = f"{sql_condition} and data_type='{data_type}'"
            if create_time_start:
                sql_condition = f"{sql_condition} and create_time >='{create_time_start}'"
            if create_time_end:
                sql_condition = f"{sql_condition} and create_time <='{create_time_end}'"
            if qc1_status:
                sql_condition = f"{sql_condition} and qc1_status={qc1_status}"
            if prc_status:
                sql_condition = f"{sql_condition} and prc_status={prc_status}"   
            if filename:
                sql_condition = f" and filename='{filename}'"  

            sql_count = f"{sql_count} {sql_condition}"
            sql_data = f"{sql_data} {sql_condition}"

            if limit > 0:
                sql_data = f"{sql_data} limit {limit}"  

            totalCount = self.db.select_one(sql_count)
            _, recs = self.db.select_many(sql_data)
            return Result.ok_data(data=from_dict_list(Level1Record, recs)).append("totalCount", totalCount['c'])

        except Exception as e:
            return Result.error(message=str(e))
        

    def get(self, **kwargs):
        '''
        parameter kwargs:
            id = [int] 

        return dict or None
        '''
        try:
            fits_id = get_parameter(kwargs, "id", -1)
            r = self.db.select_one(
                "select * from msc_level1_data where id=?", (fits_id,))

            if r:
                return Result.ok_data(data=Level1Record().from_dict(r))
            else:
                return Result.error(message=f"id:{fits_id} not found")  
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))        

    def update_proc_status(self, **kwargs):
        ''' update the status of reduction

        parameter kwargs:
            id : [int],
            status : [int]

        return csst_dfs_common.models.Result
        '''
        fits_id = get_parameter(kwargs, "id")
        status = get_parameter(kwargs, "status")
        try:
            existed = self.db.exists(
                "select * from msc_level1_data where id=?",
                (fits_id,)
            )
            if not existed:
                log.warning('%s not found' %(fits_id, ))
                return Result.error(message ='%s not found' %(fits_id, ))
            self.db.execute(
                'update msc_level1_data set prc_status=?, prc_time=? where id=?',
                (status, format_time_ms(time.time()), fits_id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def update_qc1_status(self, **kwargs):
        ''' update the status of QC1
        
        parameter kwargs:
            id : [int],
            status : [int]
        '''        
        fits_id = get_parameter(kwargs, "id")
        status = get_parameter(kwargs, "status")
        try:
            existed = self.db.exists(
                "select * from msc_level1_data where id=?",
                (fits_id,)
            )
            if not existed:
                log.warning('%s not found' %(fits_id, ))
                return Result.error(message ='%s not found' %(fits_id, ))
            self.db.execute(
                'update msc_level1_data set qc1_status=?, qc1_time=? where id=?',
                (status, format_time_ms(time.time()), fits_id)
            )  
            self.db.end() 
            return Result.ok_data()
           
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))

    def write(self, **kwargs):
        ''' insert a level1 record into database
 
        parameter kwargs:
            raw_id : [int]
            data_type : [str]
            cor_sci_id : [int]
            prc_params : [str]
            flat_id : [int]
            dark_id : [int]
            bias_id : [int]
            lamp_id : [int]
            arc_id : [int]
            sky_id : [int]            
            filename : [str]
            file_path : [str]            
            prc_status : [int]
            prc_time : [str]
            pipeline_id : [str]

        return csst_dfs_common.models.Result
        '''   
        try:
            rec = Level1Record(
                id = 0,
                raw_id = get_parameter(kwargs, "raw_id"),
                data_type = get_parameter(kwargs, "data_type"),
                cor_sci_id = get_parameter(kwargs, "cor_sci_id"),
                prc_params = get_parameter(kwargs, "prc_params"),
                flat_id = get_parameter(kwargs, "flat_id"),
                dark_id = get_parameter(kwargs, "dark_id"),
                bias_id = get_parameter(kwargs, "bias_id"),
                filename = get_parameter(kwargs, "filename"),
                file_path = get_parameter(kwargs, "file_path"),
                prc_status = get_parameter(kwargs, "prc_status", -1),
                prc_time = get_parameter(kwargs, "prc_time", format_datetime(datetime.datetime.now())),
                pipeline_id = get_parameter(kwargs, "pipeline_id")
            )
            existed = self.db.exists(
                    "select * from msc_level1_data where filename=?",
                    (rec.filename,)
                )
            if existed:
                log.error(f'{rec.filename} has already been existed')
                return Result.error(message=f'{rec.filename} has already been existed') 

            self.db.execute(
                'INSERT INTO msc_level1_data (raw_id,data_type,cor_sci_id,prc_params,flat_id,dark_id,bias_id,filename,file_path,qc1_status,prc_status,prc_time,create_time,pipeline_id) \
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (rec.raw_id, rec.data_type, rec.cor_sci_id, rec.prc_params, rec.flat_id, rec.dark_id, rec.bias_id, rec.filename, rec.file_path, -1, rec.prc_status, rec.prc_time, format_time_ms(time.time()),rec.pipeline_id,)
            )
            self.db.end()
            rec.id = self.db.last_row_id()

            return Result.ok_data(data=rec)
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))            