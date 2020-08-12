
from functools import wraps
from flask import Flask, flash,jsonify

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

def get_user_bykeyword(keyword):
    all_user=User.query.filter(User.username.like('%{keyword}%'.format(keyword=keyword))).all()
    return all_user

def get_user_ingroup(groupid):
    all_GroupMember=GroupMember.query.filter(GroupMember.group_id==groupid)
    all_user=[]
    for groupmember in all_GroupMember:
        user=User.query.filter(User.id==groupmember.user_id).all()
        all_user+=user
    return all_user

def user_to_content(user):
    content={
        'id':user.id,
        'username':user.username,
        'email':user.email,
        'password':user.password
    }
    return content

def group_to_content(group):
    context={
        'groupid':group.id,
        'groupname':group.groupname,
        'description':group.description,
        'createdtime':group.createdtime
    }
    return context

def sendmsg(str):
    context={
        'message':str
    }
    return jsonify(context)
