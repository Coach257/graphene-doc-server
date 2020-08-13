
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
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            session['username'] = request.form.get('username')
            return sendmsg('success')
    return sendmsg('fail')

# 获取当前登录用户
# tested
@app.route('/api/get_user/',methods=['POST'])
def get_user():
    user = get_user_byusername(request.form['username'])
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
        user = User.query.filter(User.username==request.form['username']).first()
        username = User.query.filter(User.username == request.form['new_username']).first()
        email = User.query.filter(User.email == request.form['new_email']).first()
        if(username):
            if(username.id!=user.id):
                return sendmsg('fail')
        if(email):
            if(email.id!=user.id):
                return sendmsg('fail')
        db.session.query(User).filter(User.username==request.form['username']).update({"password":request.form['new_password1'],
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
   user=get_user_byusername(request.form['username'])
   id=get_newid()
   newGroup=Group(id=id,groupname=request.form['groupname'],leaderid=user.id,createdtime=datetime.datetime.now(),description=request.form['description'])
   newGroupMember=GroupMember(id=id,group_id=id,user_id=user.id)
   db.session.add(newGroup)
   db.session.add(newGroupMember)
   db.session.commit()
   return sendmsg('success')

# 显示我加入的group
# tested
@app.route('/api/mygroup/',methods=['POST'])
def mygroup():
    user=get_user_byusername(request.form['username'])
    all_groupmember=GroupMember.query.filter(GroupMember.user_id==user.id)
    res=[]
    for groupmember in all_groupmember:
        group=Group.query.filter(Group.id==groupmember.group_id).first()
        res.append(group_to_content(group))
    return jsonify(res)

# 判断这个group是不是当前登录用户所创建的group
# tested
@app.route('/api/groupiscreatedbyme/',methods=['POST'])
def groupiscreatedbyme():
    user=get_user_byusername(request.form['username'])
    res=Group.query.filter(and_(Group.leaderid==user.id,Group.id==request.form['groupid'])).first()
    if(res):
        return sendmsg('yes')
    return sendmsg('no')

@app.route('/api/group_created_byme/',methods=['POST'])
def group_created_byme():
    user=get_user_byusername(request.form['username'])
    all_group=Group.query.filter(Group.leaderid==user.id).all()
    res=[]
    for group in all_group:
        res.append(group_to_content(group))
    return jsonify(res)


# 添加成员
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
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=userid,last_watch=datetime.datetime.now(),
            favorited=0)
        db.session.add(newDU)
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
    groupid=request.form['groupid']
    userid=request.form['userid']
    db.session.query(GroupMember).filter(and_(GroupMember.user_id==request.form['userid'],GroupMember.group_id==request.form['groupid'])).delete()
    #删除成员对应文档权限
    db.session.commit()
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==userid)).delete()
        db.session.commit()
    return jsonify({'message':'success'})

# 解散团队
@app.route('/api/delete_group/',methods=['POST'])
def delete_group():
    groupid=request.form['groupid']
    db.session.query(GroupMember).filter(GroupMember.group_id==request.form['groupid']).delete()
    db.session.query(Group).filter(Group.id==request.form['groupid']).delete()
    # 删除成员对应文档
    # # 删除团队文档
    db.session.commit()
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        db.session.query(DocumentUser).filter(DocumentUser.document_id==document.id).delete()
        db.session.commit()
    return jsonify({'message':'success'})
    
####################################
########## Document 操作 ###############
####################################

# 创建个人文档 (同时赋予权限)
@app.route('/api/create_personal_doc/', methods=['POST'])
def create_personal_doc():
    msg=''
    if request.method == 'POST':
        id = get_newid()
        user = User.query.filter(User.username==request.form['username']).first()
        creator_id=user.id
        now=datetime.datetime.now()
        content=request.form['content']
        msg="success"
        newDocument=Document(id=id,title=request.form['title'], 
            creator_id=creator_id,created_time=now,
            modify_right=request.form['modify_right'],
            share_right=request.form['share_right'],
            discuss_right=request.form['discuss_right'],
            content=content,recycled=0,is_occupied=0,
            group_id=0,modified_time=now)
        db.session.add(newDocument)
        db.session.commit()

        id=get_newid()
        newDU=DocumentUser(id=id,document_id=newDocument.id,
            user_id=user.id,last_watch=datetime.datetime.now(),
            favorited=0)
        db.session.add(newDU)
        db.session.commit()
        # # 赋予创建者以文档的全部权限
        # share_right=1
        # watch_right=1
        # modify_right=1
        # delete_right=1
        # discuss_right=1
        # document=newDocument
        # newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
        #     share_right=share_right,watch_right=watch_right,modify_right=modify_right,
        #     delete_right=delete_right,discuss_right=discuss_right
        # )
        # db.session.add(newDocumentUser)
        # db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 创建团队文档 (同时赋予权限)
@app.route('/api/create_group_doc/', methods=['POST'])
def create_group_doc():
    msg=''
    if request.method == 'POST':
        id = get_newid()
        user = User.query.filter(User.username==request.form['username']).first()
        creator_id=user.id
        now=datetime.datetime.now()
        content=request.form['content']
        group_id=request.form['group_id']
        msg="success"
        newDocument=Document(id=id,title=request.form['title'], 
            creator_id=creator_id,created_time=now,
            modify_right=request.form['modify_right'],
            share_right=request.form['share_right'],
            discuss_right=request.form['discuss_right'],
            content=content,recycled=0,is_occupied=0,
            group_id=group_id,modified_time=now)
        db.session.add(newDocument)
        db.session.commit()

        id=get_newid()
        i=1
        all_member=GroupMember.query.filter(GroupMember.group_id==group_id).all()
        for member in all_member:
            newDU=DocumentUser(id=id+i,document_id=newDocument.id,
            user_id=member.id,last_watch=datetime.datetime.now(),
            favorited=0)
            i=i+1
            db.session.add(newDU)
            db.session.commit()

        # # 赋予创建者以文档的全部权限
        # share_right=1
        # watch_right=1
        # modify_right=1
        # delete_right=1
        # discuss_right=1
        # document=newDocument
        # newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
        #     share_right=share_right,watch_right=watch_right,modify_right=modify_right,
        #     delete_right=delete_right,discuss_right=discuss_right
        # )
        # db.session.add(newDocumentUser)
        # db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 获取我创建的所有文档的信息
@app.route('/api/my_created_docs/',methods=['POST'])
def my_created_docs():
    user=User.query.filter(User.username==request.form['username']).first()
    all_document=Document.query.filter(and_(Document.creator_id==user.id,Document.recycled==0)).all()
    res=[]
    for document in all_document:
        res.append(document_to_content(document))
    return jsonify(res)

@app.route('/api/my_deleted_docs/',methods=['POST'])
def my_deleted_docs():
    user=User.query.filter(User.username==request.form['username']).first()
    all_document=Document.query.filter(and_(Document.creator_id==user.id,Document.recycled==1)).all()
    res=[]
    for document in all_document:
        res.append(document_to_content(document))
    return jsonify(res)

# 获取文档
@app.route('/api/get_doccontent/', methods=['POST'])
def get_doccontent():
    msg=''
    mcontent=''
    mtime=datetime.datetime.now()
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user=User.query.filter(User.username==request.form['username']).first()
        if (document==None) or (user==None):
            msg="fail"
            mcontent=""
            response={
                'message':msg,
                'content':mcontent
            }
            return jsonify(response)
        DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        mtime=DUlink.last_watch
        # 判断用户是否有权限查看该文档
        # 初步完善
        # TODO: 目前只有创建者能查看文档(已修正)
        # TODO: 目前任何参与者都可以查看文档
        if (document!=None) and (DUlink!=None):
            msg="success"
            mcontent=document.content
            now=datetime.datetime.now()
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"last_watch":now})
            db.session.commit()
            DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
            mtime=DUlink.last_watch
        else:
            msg="fail"
            mcontent=""
    response={
        'message':msg,
        'content':mcontent,
        'time':mtime
    }
    return jsonify(response)


# 修改文档
@app.route('/api/modify_doc/', methods=['POST'])
def modify_doc():
    msg=''
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        # TODO: 目前只有创建者能修改文档
        if (document!=None) and (str(document.creator_id)==str(user.id)):
            msg="success"
            now=datetime.datetime.now()
            content=request.form['content']
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"content":content,
                "modified_time":now
            })
            db.session.commit()
        else:
            msg="fail"
    response={
        'message':msg
    }
    return jsonify(response)

# 文档分享
@app.route('/api/share_to/',methods=['POST'])
def share_to():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        target_user=User.query.filter(User.username==request.form['target_user']).first()
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=target_user,last_watch=datetime.datetime.now(),
            favorited=0)
        db.session.add(newDU)
        db.session.commit()

# 收藏文档
@app.route('/api/favor_doc/', methods=['POST'])
def favor_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        if document!=None and document.favorited==0:
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"favorited":1})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)


# 文档删除到回收站中
@app.route('/api/recycle_doc/', methods=['POST'])
def recycle_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # if (document!=None) and (DUlink.delete_right==1)and (document.recycled==0):
        if (document!=None) and (document.recycled==0) and (document.creator_id==user.id):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":1})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 文件从回收站中删除变成二级删除状态
@app.route('/api/del_doc/', methods=['POST'])
def del_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # if (document!=None) and (DUlink.delete_right==1) and (document.recycled==1):
        if (document!=None) and (document.recycled==1) and (document.creator_id==user.id):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":2})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 文档从回收站中恢复
@app.route('/api/recover_doc/', methods=['POST'])
def recover_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # if (document!=None) and (DUlink.delete_right==1)and (document.recycled==0):
        if (document!=None) and (document.recycled==1) and (document.creator_id==user.id):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":0})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 文档彻底删除操作
@app.route('/api/del_complete_doc/', methods=['POST'])
def del_complete_doc():
    msg=''
    if request.method=='POST':
        id=get_newid()
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        print(document!=None)
        print(document.recycled)
        print(DUlink.delete_right)
        #if (document!=None) and (document.recycled==1) and (DUlink.delete_right==1):
        if (document!=None) and (document.recycled==1) and (document.creator_id==user.id):
            msg='success'
            db.session.query(DocumentUser).filter(DocumentUser.document_id==document.id).delete()
            db.session.commit()
            db.session.query(Comment).filter(Comment.document_id==document.id).delete()
            db.session.commit()
            db.session.query(Document).filter(Document.id==document.id).delete()
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

# # 授予权限
# @app.route('/api/grant_right/', methods=['POST'])
# def grant_right():
#     msg=''
#     if request.method=='POST':
#         id=get_newid()
#         document = Document.query.filter(Document.id == request.form['DocumentID']).first()
#         user = User.query.filter(User.username==request.form['username']).first()
#         share_right=request.form['share_right']
#         # watch_right=request.form['watch_right']
#         modify_right=request.form['modify_right']
#         # delete_right=request.form['delete_right']
#         #delete_right=0
#         discuss_right=request.form['discuss_right']
#         newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
#             share_right=share_right,watch_right=watch_right,modify_right=modify_right,
#             delete_right=delete_right,discuss_right=discuss_right
#         )
#         db.session.add(newDocumentUser)
#         db.session.commit()
#         response={
#             'message':'grant right success'
#         }
#         return jsonify(response)

# 文档创建者修改权限
@app.route('/api/modify_right/', methods=['POST'])
def modify_right():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        share_right=request.form['share_right']
        # watch_right=request.form['watch_right']
        modify_right=request.form['modify_right']
        # delete_right=request.form['delete_right']
        discuss_right=request.form['discuss_right']
        db.session.query(Document).filter(Document.id==document.id).update({"share_right":share_right,
            "modify_right":modify_right,"discuss_right":discuss_right})
        #     "watch_right":watch_right,"modify_right":modify_right,"delete_right":delete_right,"discuss_right":discuss_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"share_right":share_right,
        #     "watch_right":watch_right,"modify_right":modify_right,"delete_right":delete_right,"discuss_right":discuss_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"watch_right":watch_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"modify_right":modify_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"delete_right":delete_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"discuss_right":discuss_right})
        db.session.commit()
        response={
            'message':'modify right success'
        }
        return jsonify(response)

####################################
########## 评论 操作 ###############
####################################

# 创建评论
@app.route('/api/create_comment/', methods=['POST'])
def create_comment():
    msg=''
    if request.method == 'POST':
        id=get_newid()
        user = User.query.filter(User.username==request.form['username']).first()
        creator_id=user.id
        document_id=request.form['DocumentID']
        now=datetime.datetime.now()
        content=request.form['content']
        msg="success"
        newComment=Comment(id=id,document_id=document_id,creator_id=creator_id,content=content,created_time=now)
        db.session.add(newComment)
        db.session.commit()
        response={
            'message':'create comment success'
        }
        return jsonify(response)

# 获取文档的所有评论
@app.route('/api/get_all_comment', methods=['POST'])
def get_all_comment():
    all_comment=Comment.query.filter(Comment.document_id==request.form['DocumentID'])
    res=[]
    for comment in all_comment:
        res.append(comment_to_content(comment))
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug = True)
