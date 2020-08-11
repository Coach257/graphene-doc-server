
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_,not_
from models import *
from manage import *
from flask_cors import CORS
import config
from datetime import datetime

app = Flask(__name__,
            static_folder = "../frontend/dist/static",
            template_folder = "../frontend/dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(config)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return render_template("index.html")

#登录
@app.route('/api/login/', methods=['POST'])
def login():
    msg=''
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['username'] = request.form.get('username')
            msg='success'
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

#获取当前登录用户的用户名
@app.route('/api/get_user/',methods=['GET'])
def get_user():
    if session['username']==None: 
        response={
            'username':'',
            'password':'',
            'email':''
        }
    else:
        user = get_user_byusername(session['username'])
        response={
            'username':user.username,
            'password':user.password,
            'email':user.email
        }
    return jsonify(response)

@app.route('/api/logout/',methods=['GET'])
def logout():
    msg='退出成功'
    session['username']=None
    response={
        'message':msg
    }
    return jsonify(response)

#注册
@app.route('/api/regist/', methods=['POST'])
def regist():
    msg=''
    if request.method == 'POST':
        username = User.query.filter(User.username == request.form['username']).first()
        email = User.query.filter(User.email == request.form['email']).first()
        if(username or email):
            msg='用户名或邮箱不能重复！'
        else:
            msg="成功注册！"
            id=get_newid()
            newUser=User(id=id, username=request.form['username'], password=request.form['password'], email=request.form['email'])
            db.session.add(newUser)
            db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

@app.route('/api/getalluser/',methods=['GET'])
def getalluser():
    all_user=User.query.all()
    res=[]
    context={}
    for user in all_user:
        context={
            'username':user.username,
            'password':user.password,
            'email':user.email
        }
        res.append(context)
    return jsonify(res)


# 修改密码
@app.route('/api/modifypwd/', methods=['POST'])
def modifypwd():
    msg = None
    if request.method == 'POST':
        user = User.query.filter(User.username==session['username']).first()
        session['password'] = user.password
        if (session['password']!=request.form['oldpassword']):
            msg = '原密码错误！'
        elif(request.form['newpassword1']!=request.form['newpassword2']):
            msg = '两次密码不一致！'
        else:
            session['password']=request.form['newpassword1']
            get_user_byusername(session['username']).update({"password":request.form['newpassword1']})
            db.session.commit()
            msg = 'success'

    response={
        'message':msg
    }
    return jsonify(response)

@app.route('/api/creategroup/',methods=['POST'])
def creategroup():
   user=get_user_byusername(session['username'])
   newGroup=Group(groupname=request.form['groupname'],leaderid=user.id,createdtime=datetime.datetime.now(),description=request.form['description'])
   db.session.add(newGroup)
   db.session.commit()
   response={
       'message':'创建团队成功！'
   }
   return jsonify(response)

####################################
##########Document操作###############
####################################

#创建文档
@app.route('/api/create_doc/', methods=['POST'])
def create_doc():
    msg=''
    if request.method == 'POST':
        user = User.query.filter(User.username==session['username']).first()
        creator_id=user.id
        now=datetime.now()
        content=request.form['content']
        msg="成功创建文档！"
        id = get_newid()
        newDocument=Document(id=id,title=request.form['title'], creator_id=creator_id,created_time=now,content=content)
        db.session.add(newDocument)
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

#获取文档
@app.route('/api/get_doccontent/', methods=['POST'])
def get_doccontent():
    msg=''
    mcontent=''
    if request.method == 'POST':
        document = Document.query.filter(Document.title == request.form['title']).first()
        user = User.query.filter(User.username==session['username']).first()
        #判断用户是否有权限查看该文档
        #未完善，只是初步的判断
        msg='ok'
        #print(str(document.creator_id)+'/')
        #print(str(user.id)+'/')
        if (document!=None) and (str(document.creator_id)==str(user.id)):
            msg="成功找到该文档"
            mcontent=document.content
        else:
            msg="没有找到该文档"
            mcontent=""
    response={
        'message':msg,
        'content':mcontent
    }
    return jsonify(response)

'''
#修改文档
@app.route('/api/modify_doc/', methods=['POST'])
def modify_doc():
    msg=''
    if request.method == 'POST':
        title = Document.query.filter(Document.title == request.form['title']).first()
        user = User.query.filter(User.username==session['username']).first()
        creator_id=user.id
        now=datetime.now()
        content=request.form['content']
        msg="成功创建文档！"
        id = get_newid()
        newDocument=Document(id=id,title=request.form['title'], creator_id=creator_id,created_time=now,content=content)
        db.session.add(newDocument)
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)
'''

if __name__ == '__main__':
    app.run(debug = True)
