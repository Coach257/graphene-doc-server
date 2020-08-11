import os
import pymysql

pymysql.install_as_MySQLdb()
base_dir=os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "mysql://root:root@49.235.221.218:3306/xxq"
SQLALCHEMY_TRACK_MODIFICATIONS = False