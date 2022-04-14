import os
import logging
import time, datetime
import shutil
from traceback import print_stack

from ..common.db import DBClient
from ..common.utils import *
from csst_dfs_commons.models import Result
from csst_dfs_commons.models.common import from_dict_list
from csst_dfs_commons.models.msc import MSCLevel2CatalogRecord

log = logging.getLogger('csst')

class Level2CatalogApi(object):
    def __init__(self, sub_system = "msc"):
        self.sub_system = sub_system
        self.root_dir = os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst")
        self.db = DBClient()

    def find(self, **kwargs):
        ''' retrieve level1 records from database

        parameter kwargs:
            obs_id: [str]
            detector_no: [str]
            obs_time : (start, end),
            filename: [str]
            limit: limits returns the number of records,default 0:no-limit

        return: csst_dfs_common.models.Result
        '''
        try:
            obs_id = get_parameter(kwargs, "obs_id")
            detector_no = get_parameter(kwargs, "detector_no")
            obs_time_start = get_parameter(kwargs, "obs_time", [None, None])[0]
            obs_time_end = get_parameter(kwargs, "obs_time", [None, None])[1]
            limit = get_parameter(kwargs, "limit", 0)

            sql_count = "select count(*) as c from msc_level2_catalog where 1=1"
            sql_data = f"select * from msc_level2_catalog where 1=1"

            sql_condition = "" 
            if obs_id:
                sql_condition = f"{sql_condition} and obs_id='{obs_id}'"
            if detector_no:
                sql_condition = f"{sql_condition} and detector_no='{detector_no}'"
            if obs_time_start:
                sql_condition = f"{sql_condition} and obs_time >='{obs_time_start}'"
            if obs_time_end:
                sql_condition = f"{sql_condition} and obs_time <='{obs_time_end}'"

            sql_count = f"{sql_count} {sql_condition}"
            sql_data = f"{sql_data} {sql_condition}"

            if limit > 0:
                sql_data = f"{sql_data} limit {limit}"  

            totalCount = self.db.select_one(sql_count)
            _, recs = self.db.select_many(sql_data)
            return Result.ok_data(data=from_dict_list(MSCLevel2CatalogRecord, recs)).append("totalCount", totalCount['c'])

        except Exception as e:
            return Result.error(message=str(e))

    def write(self, records):
       
        try:
            recordStrs = []
            for recordStr in records:
                recordStrs.append(f"({recordStr})")
            if recordStrs:
                self.db.execute(
                f"insert into msc_level2_catalog values {','.join(recordStrs)}" 
                )
                self.db.end()

            return Result.ok_data()
        except Exception as e:
            print_stack()
            log.error(e)
            return Result.error(message=str(e))            