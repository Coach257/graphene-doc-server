import os
import pymysql

pymysql.install_as_MySQLdb()
base_dir=os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "mysql://root:root@49.235.221.218:3306/xxq?charset=utf8"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_POOL_SIZE = 1024
SQLALCHEMY_POOL_TIMEOUT = 90
SQLALCHEMY_POOL_RECYCLE = 3
SQLALCHEMY_MAX_OVERFLOW = 1024