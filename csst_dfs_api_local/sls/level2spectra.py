import os
import logging
import time, datetime
import shutil

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.sls import Level2Spectra
from csst_dfs_commons.models.common import from_dict_list

log = logging.getLogger('csst')

class Level2SpectraApi(object):
    def __init__(self, sub_system = "sls"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()

    def find(self, **kwargs):
        ''' retrieve records from database

        parameter kwargs:
            level1_id: [int]
            spectra_id: [str]
            create_time : (start, end),
            qc1_status : [int],
            prc_status : [int],
            filename: [str]
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            level1_id = get_parameter(kwargs, "level1_id", 0)
            spectra_id = get_parameter(kwargs, "spectra_id")
            create_time_start = get_parameter(kwargs, "create_time", [None, None])[0]
            create_time_end = get_parameter(kwargs, "create_time", [None, None])[1]
            qc1_status = get_parameter(kwargs, "qc1_status")
            prc_status = get_parameter(kwargs, "prc_status")
            filename = get_parameter(kwargs, "filename")
            limit = get_parameter(kwargs, "limit", 0)

            sql_count = "select count(*) as c from sls_level2_spectra where 1=1"
            sql_data = f"select * from sls_level2_spectra where 1=1"

            sql_condition = "" 
            if level1_id > 0:
                sql_condition = f"{sql_condition} and level1_id={level1_id}"
            if spectra_id:
                sql_condition = f"{sql_condition} and spectra_id='{spectra_id}'"
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
            return Result.ok_data(data=from_dict_list(Level2Spectra, recs)).append("totalCount", totalCount['c'])

        except Exception as e:
            return Result.error(message=str(e))
        
    def get(self, **kwargs):
        '''
        parameter kwargs:
            id = [int]
        return csst_dfs_common.models.Result
        '''
        try:
            id = get_parameter(kwargs, "id", -1)
            r = self.db.select_one(
                "select * from sls_level2_spectra where id=?", (id,))
            if r:
                return Result.ok_data(data=Level2Spectra().from_dict(r))
            else:
                return Result.error(message=f"id:{id} not found")  
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
                "select * from sls_level2_spectra where id=?",
                (fits_id,)
            )
            if not existed:
                log.warning('%s not found' %(fits_id, ))
                return Result.error(message ='%s not found' %(fits_id, ))
            self.db.execute(
                'update sls_level2_spectra set prc_status=?, prc_time=? where id=?',
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
                "select * from sls_level2_spectra where id=?",
                (fits_id,)
            )
            if not existed:
                log.warning('%s not found' %(fits_id, ))
                return Result.error(message ='%s not found' %(fits_id, ))
            self.db.execute(
                'update sls_level2_spectra set qc1_status=?, qc1_time=? where id=?',
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
            level1_id: [int]
            spectra_id : [str]
            region : [str]
            filename : [str]
            file_path : [str]            
            prc_status : [int]
            prc_time : [str]
            pipeline_id : [str]

        return csst_dfs_common.models.Result
        '''   
        try:
            rec = Level2Spectra(
                id = 0,
                level1_id = get_parameter(kwargs, "level1_id"),
                spectra_id = get_parameter(kwargs, "spectra_id"),
                region = get_parameter(kwargs, "region"),
                filename = get_parameter(kwargs, "filename"),
                file_path = get_parameter(kwargs, "file_path"),
                prc_status = get_parameter(kwargs, "prc_status", -1),
                prc_time = get_parameter(kwargs, "prc_time", format_datetime(datetime.now())),
                pipeline_id = get_parameter(kwargs, "pipeline_id")
            )
            existed = self.db.exists(
                    "select * from sls_level2_spectra where filename=?",
                    (rec.filename,)
                )
            if existed:
                log.error(f'{rec.filename} has already been existed')
                return Result.error(message=f'{rec.filename} has already been existed') 

            self.db.execute(
                'INSERT INTO sls_level2_spectra (level1_id,spectra_id,region,filename,file_path,qc1_status,prc_status,prc_time,create_time,pipeline_id) \
                    VALUES(?,?,?,?,?,?,?,?,?,?)',
                (rec.level1_id, rec.spectra_id, rec.region, rec.filename, rec.file_path, -1, rec.prc_status, rec.prc_time, format_time_ms(time.time()),rec.pipeline_id,)
            )
            self.db.end()
            rec.id = self.db.last_row_id()

            return Result.ok_data(data=rec)
        except Exception as e:
            log.error(e)
            return Result.error(message=str(e))            