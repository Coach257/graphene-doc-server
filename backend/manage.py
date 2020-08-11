
from functools import wraps
from flask import Flask, flash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_,not_
from models import *
import time
import config

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)

def get_newid():
    time_now = int(time.time())
    #转换成localtime
    time_local = time.localtime(time_now)
    #转换成新的时间格式(2016-05-09 18:59:20)
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
    id=time.mktime(time.strptime(dt,"%Y-%m-%d %H:%M:%S"))
    return id

def valid_login(username, password):
    user = User.query.filter(and_(User.username == username, User.password == password)).first()
    if user:
        return True
    else:
        return False

def get_user_byusername(username):
    user = User.query.filter(User.username==username).first()
    return user