import os
import datetime
import sqlite3
from DBUtils.PersistentDB import PersistentDB
from .utils import singleton

import logging

log = logging.getLogger('csst')

@singleton
class DBClient(object):
    def __init__(self):
        db_path = os.path.join(os.getenv("CSST_LOCAL_FILE_ROOT", "/opt/temp/csst"), "csst.sqlite")

        self.inited = os.path.exists(db_path)
        self.pool = PersistentDB(sqlite3, maxusage=2, database=db_path)
        
        log.info("Creating connection pool with host = [%s]", db_path)

        self._conn = None
        self._cursor = None
        self.__get_conn()

        if not self.inited:
            self.__init_db()
    
    def __del__(self):
        self.close()

    def __get_conn(self):
        self._conn = self.pool.connection()
        self._cursor = self._conn.cursor()
        
    def __execute(self, sql, param=()):
        count = self._cursor.execute(sql, param)
        return count
    
    def __init_db(self):
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "db.sql")) as f:
            self.execute(f.read())

    def select_one(self, sql, param=()):
        """查询单个结果"""
        count = self.__execute(sql, param)
        result = self._cursor.fetchone()
        """:type result:dict"""
        result = self.__dict_datetime_obj_to_str(result)
        return count, result

    def select_many(self, sql, param=()):
        """
        查询多个结果
        :param sql: qsl语句
        :param param: sql参数
        :return: 结果数量和查询结果集
        """
        count = self.__execute(sql, param)
        result = self._cursor.fetchall()
        """:type result:list"""
        [self.__dict_datetime_obj_to_str(row_dict) for row_dict in result]
        return count, result

    def execute(self, sql, param=()):
        count = self.__execute(sql, param)
        return count

    def begin(self):
        """开启事务"""
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """结束事务"""
        if option == 'commit':
            self._conn.autocommit()
        else:
            self._conn.rollback()    
    
    def __dict_datetime_obj_to_str(self, result_dict):
        """把字典里面的datatime对象转成字符串，使json转换不出错"""
        if result_dict and isinstance(result_dict, tuple):
            result_replace = [v.__str__() for  v in result_dict if isinstance(v, datetime.datetime)]
            return result_replace

        if result_dict and isinstance(result_dict, dict):
            result_replace = {k: v.__str__() for k, v in result_dict.items() if isinstance(v, datetime.datetime)}
            result_dict.update(result_replace)            
        return result_dict

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception as e:
            log.error(e)
