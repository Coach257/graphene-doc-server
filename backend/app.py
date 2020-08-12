
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_,not_
from models import *
from manage import *
from flask_cors import CORS
import config
import datetime,time
app = Flask(__name__,
            static_folder = "../frontend/dist/static",
            template_folder = "../frontend/dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(config)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return render_template("index.html")

####################################
########## User 操作 ###############
####################################

#登录
# tested
@app.route('/api/login/', methods=['POST'])
def login():
    msg=''
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['username'] = request.form.get('username')
            return sendmsg('success')
    return sendmsg('fail')

#获取当前登录用户
# tested
@app.route('/api/get_user/',methods=['GET'])
def get_user():
    if session==None or session['username']==None or session['username']=='' : 
        response=user_to_content(User(0,'','',''))
    else:
        user = get_user_byusername(session['username'])
        response=user_to_content(user)
    return jsonify(response)

# tested
@app.route('/api/get_user_byid/',methods=['POST'])
def get_user_byid():
    user=User.query.filter(User.id==request.form['userid']).first()
    return jsonify(user_to_content(user))

# tested
@app.route('/api/logout/',methods=['GET'])
def logout():
    session['username']=None
    return sendmsg('success')

# 注册
@app.route('/api/regist/', methods=['POST'])
def regist():
    if request.method == 'POST':
        username = User.query.filter(User.username == request.form['username']).first()
        email = User.query.filter(User.email == request.form['email']).first()
        if(username or email):
            return sendmsg('fail')
        else:
            id=get_newid()
            newUser=User(id=id, username=request.form['username'], password=request.form['password'], email=request.form['email'])
            db.session.add(newUser)
            db.session.commit()
    return sendmsg('success')

# tested
@app.route('/api/getalluser/',methods=['GET'])
def getalluser():
    all_user=User.query.all()
    res=[]
    for user in all_user:
        res.append(user_to_content(user))
    return jsonify(res)


# 修改User Info
@app.route('/api/modify_user_info/', methods=['POST'])
def modify_user_info():
    if request.method == 'POST':
        user = User.query.filter(User.username==session['username']).first()
        if (user.password!=request.form['oldpassword']):
            return sendmsg('fail')
        else:
            db.session.query(User).filter(User.username==session['username']).update({"password":request.form['new_password1'],
                "username":request.form['new_username'],
                "email":request.form['new_email']})
            # db.session.query(User).filter(User.username==session['username']).update({"username":request.form['new_username']})
            # db.session.query(User).filter(User.username==session['username']).update({"email":request.form['new_email']})
            db.session.commit()
            session['username']=request.form['new_username']
    return sendmsg('success')


####################################
########## Group 操作 ###############
####################################

# 已登录的用户创建group，设置group的简介
# tested
@app.route('/api/creategroup/',methods=['POST'])
def creategroup():
   user=get_user_byusername(session['username'])
   id=get_newid()
   newGroup=Group(id=id,groupname=request.form['groupname'],leaderid=user.id,createdtime=datetime.datetime.now(),description=request.form['description'])
   newGroupMember=GroupMember(id=id,group_id=id,user_id=user.id)
   db.session.add(newGroup)
   db.session.add(newGroupMember)
   db.session.commit()
   return sendmsg('success')

# 显示我加入的group
# tested
@app.route('/api/mygroup/',methods=['GET'])
def mygroup():
    user=get_user_byusername(session['username'])
    all_groupmember=GroupMember.query.filter(GroupMember.user_id==user.id)
    res=[]
    for groupmember in all_groupmember:
        group=Group.query.filter(Group.id==groupmember.group_id).first()
        res.append(group_to_content(group))
    return jsonify(res)

# 判断这个group是不是当前登录用户所创建的group
# tested
@app.route('/api/groupiscreatedbyme',methods=['POST'])
def groupiscreatedbyme():
    user=get_user_byusername(session['username'])
    res=Group.query.filter(and_(Group.leaderid==user.id,Group.id==request.form['groupid'])).first()
    if(res):
        return sendmsg('yes')
    return sendmsg('no')

# 在我的group中添加用户，这里的用户是前端判断好的不在该group中的user
# tested
@app.route('/api/addgroupmember/',methods=['POST'])
def addgroupmember():
    userid=request.form['userid']
    groupid=request.form['groupid']
    id=get_newid()
    newGroupMember=GroupMember(id=id,user_id=userid,group_id=groupid)
    db.session.add(newGroupMember)
    db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

# 团队创建者想要邀请需要先检索用户，根据用户名检索，返回所有不在该团队中的检索用户
# tested
@app.route('/api/queryuser/',methods=['POST'])
def queryuser():
    keyword=request.form['keyword']
    groupid=request.form['groupid']
    res=[]
    all_user=get_user_bykeyword(keyword)
    all_group_user=get_user_ingroup(groupid)
    for user in all_user:
        check=1
        for group_user in all_group_user:
            if group_user.id==user.id:
                check=0
                continue
        if check==1:
            res.append(user_to_content(user))
    return jsonify(res)

# 显示该团队下的成员
# tested
@app.route('/api/get_user_bygroup/',methods=['POST'])
def get_user_bygroup():
    all_group_user=get_user_ingroup(request.form['groupid'])
    res=[]
    for user in all_group_user:
       res.append(user_to_content(user))
    return jsonify(res)

# 删除成员
@app.route('/api/delete_user',methods=['POST'])
def delete_user():
    db.session.query(GroupMember).filter(and_(GroupMember.user_id==request.form['userid'],GroupMember.group_id==request.form['groupid'])).delete()
    #删除成员对应文档权限
    db.session.commit()
    return jsonify({'message':'success'})

# 解散团队
@app.route('/api/delete_group/',methods=['POST'])
def delete_group():
   db.session.query(GroupMember).filter(GroupMember.group_id==request.form['groupid']).delete()
   db.session.query(Group).filter(Group.id==request.form['groupid']).delete()
   #删除成员对应文档
   #删除团队文档
   db.session.commit()
   return jsonify({'message':'success'})

####################################
########## Document操作 ###############
####################################

# 创建文档
@app.route('/api/create_doc/', methods=['POST'])
def create_doc():
    msg=''
    if request.method == 'POST':
        user = User.query.filter(User.username==session['username']).first()
        creator_id=user.id
        now=datetime.datetime.now()
        content=request.form['content']
        msg="success"
        id = get_newid()
        newDocument=Document(id=id,title=request.form['title'], creator_id=creator_id,created_time=now,content=content,recycled=0)
        db.session.add(newDocument)
        db.session.commit()

         #赋予创建者以文档的全部权限
        share_right=1
        watch_right=1
        modify_right=1
        delete_right=1
        discuss_right=1
        document=newDocument
        newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
            share_right=share_right,watch_right=watch_right,modify_right=modify_right,
            delete_right=delete_right,discuss_right=discuss_right
        )
        db.session.add(newDocumentUser)
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 获取文档
@app.route('/api/get_doccontent/', methods=['POST'])
def get_doccontent():
    msg=''
    mcontent=''
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['id']).first()
        user = User.query.filter(User.username==session['username']).first()
        # 判断用户是否有权限查看该文档
        # 未完善，只是初步的判断
        msg='ok'
        # print(str(document.creator_id)+'/')
        # print(str(user.id)+'/')
        if (document!=None) and (str(document.creator_id)==str(user.id)):
            msg="success"
            mcontent=document.content
        else:
            msg="fail"
            mcontent=""
    response={
        'message':msg,
        'content':mcontent
    }
    return jsonify(response)


# 修改文档
@app.route('/api/modify_doc/', methods=['POST'])
def modify_doc():
    msg=''
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==session['username']).first()
        if (document!=None) and (str(document.creator_id)==str(user.id)):
            msg="success"
            now=datetime.datetime.now()
            content=request.form['content']
            id = get_newid()
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"content":content})
            #修改时间更新
            #待解决，因为缺少修改时间这个字段
            #db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"content":content})
            db.session.commit()
        else:
            msg="fail"
    response={
        'message':msg
    }
    return jsonify(response)

# 文档删除到回收站中
@app.route('/api/recycle_doc/', methods=['POST'])
def recycle_doc():
    msg=''
    if request.method=='POST':
        id=get_newid()
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==session['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        if (document!=None) and (DUlink.delete_right==1):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":1})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

####################################
########## 权限 操作 ###############
####################################

# 1：有权限
# 0：无权限
# 创建者直接权限全给
# 只有创建者才有给别人授予权限的权利

# 授予权限
@app.route('/api/grant_right/', methods=['POST'])
def grant_right():
    msg=''
    if request.method=='POST':
        id=get_newid()
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        share_right=request.form['share_right']
        watch_right=request.form['watch_right']
        modify_right=request.form['modify_right']
        delete_right=request.form['delete_right']
        discuss_right=request.form['discuss_right']
        newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
            share_right=share_right,watch_right=watch_right,modify_right=modify_right,
            delete_right=delete_right,discuss_right=discuss_right
        )
        db.session.add(newDocumentUser)
        db.session.commit()
        response={
            'message':'grant right success'
        }
        return jsonify(response)

# 修改权限
@app.route('/api/modify_right/', methods=['POST'])
def modify_right():
    msg=''
    if request.method=='POST':
        
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()

        share_right=request.form['share_right']
        watch_right=request.form['watch_right']
        modify_right=request.form['modify_right']
        delete_right=request.form['delete_right']
        discuss_right=request.form['discuss_right']
        db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"share_right":share_right,
            "watch_right":watch_right,"modify_right":modify_right,"delete_right":delete_right,"discuss_right":discuss_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"watch_right":watch_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"modify_right":modify_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"delete_right":delete_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"discuss_right":discuss_right})
        db.session.commit()
        response={
            'message':'modify right success'
        }
        return jsonify(response)


if __name__ == '__main__':
    app.run(debug = True)
