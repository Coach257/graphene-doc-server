
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
            newUser=User(id=id, username=request.form['username'], password=request.form['password'],
                email=request.form['email'])
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
            "email":request.form['new_email'],
            "description":request.form['new_description']})
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
    all_groupmember=GroupMember.query.filter(GroupMember.user_id==user.id).all()
    res=[]
    for groupmember in all_groupmember:
        group=Group.query.filter(Group.id==groupmember.group_id).first()
        if(group.leaderid!=user.id):
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

@app.route('/api/search_group/',methods=['POST'])
def search_group():
    user=User.query.filter(User.username==request.form['username']).first()
    keyword=request.form['keyword']
    res=[]
    all_group=Group.query.filter(Group.groupname.like('%{keyword}%'.format(keyword=keyword))).all()
    for group in all_group:
        gm=GroupMember.query.filter(and_(GroupMember.group_id==group.id,GroupMember.user_id==user.id)).first()
        if(gm):
           continue
        res.append(group_to_content(group))
    return jsonify(res)

@app.route('/api/group_created_byme/',methods=['POST'])
def group_created_byme():
    user=get_user_byusername(request.form['username'])
    all_group=Group.query.filter(Group.leaderid==user.id).all()
    res=[]
    for group in all_group:
        res.append(group_to_content(group))
    return jsonify(res)


# 作为团队的管理者，添加成员，在被接受端选择接受邀请时加人，给leader发一条消息
# 在我的group中添加用户，这里的用户是前端判断好的不在该group中的user
@app.route('/api/addgroupmember/',methods=['POST'])
def addgroupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    id=get_newid()
    newGroupMember=GroupMember(id=id,user_id=userid,group_id=groupid)
    db.session.add(newGroupMember)
    db.session.commit()

    # 发送消息
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=send_time+", "+user.username+"通过了你的邀请，加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=userid,receiver_id=group.leaderid,document_id=0,
        group_id=groupid,send_time=now,content=content,type=1
    )
    db.session.add(new_notice)
    db.session.commit()

    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=userid,last_watch=0,
            favorited=0,type=1,modified_time=0)
        db.session.add(newDU)
        db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

# 团队管理者向我发送了加入团队邀请，我拒绝了
@app.route('/api/refuse_groupmember/',methods=['POST'])
def refuse_groupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()

    # 发送消息
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=send_time+", "+user.username+"拒绝了你的邀请，不加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=userid,receiver_id=group.leaderid,document_id=0,
        group_id=groupid,send_time=now,content=content,type=5
    )
    db.session.add(new_notice)
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
            content={
                'id':user.id,
                'username':user.username,
                'email':user.email
            }
            res.append(content)
    return jsonify(res)

# 团队的leader邀请加入团队(发送邀请信息)
@app.route('/api/invite_user/',methods=['POST'])
def invite_user():
    group_id=request.form['group_id']
    group=Group.query.filter(Group.id==group_id).first()
    user_id=request.form['user_id']
    sender_id=User.query.filter(User.username==request.form['leader_username']).first().id
    sender=User.query.filter(User.id==sender_id).first()
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=send_time+", "+sender.username+"邀请你加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=sender_id,receiver_id=user_id,document_id=0,
        group_id=group_id,send_time=now,content=content,type=2
    )
    db.session.add(new_notice)
    db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

# 团队外用户申请加入某团队
@app.route('/api/apply_in_group/',methods=['POST'])
def apply_in_group():
    user=User.query.filter(User.username==request.form['username']).first()
    group=Group.query.filter(Group.groupname==request.form['groupname']).first()
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=send_time+", "+user.username+"申请加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=user.id,receiver_id=group.leaderid,document_id=0,
        group_id=group.id,send_time=now,content=content,type=6
    )
    db.session.add(new_notice)
    db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)


# 作为团队leader，收到了来自用户的申请，我选择通过他的申请，加人，给申请人发一条消息
# 在我的group中添加用户，这里的用户是前端判断好的不在该group中的user
@app.route('/api/accept_application_addgroupmember/',methods=['POST'])
def accept_application_addgroupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    leader=User.query.filter(User.id==group.leaderid).first()
    id=get_newid()
    newGroupMember=GroupMember(id=id,user_id=userid,group_id=groupid)
    db.session.add(newGroupMember)
    db.session.commit()

    # 发送消息
    id=id+1
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=send_time+", "+leader.username+"通过了你的申请，你已加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=leader.id,receiver_id=user.id,document_id=0,
        group_id=groupid,send_time=now,content=content,type=7
    )
    db.session.add(new_notice)
    db.session.commit()

    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=userid,last_watch=0,
            favorited=0,type=1,modified_time=0)
        db.session.add(newDU)
        db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

# 作为团队leader，收到了来自用户的申请，我选择拒绝他的申请，不加人，给申请人发一条消息
@app.route('/api/refuse_application_addgroupmember/',methods=['POST'])
def refuse_application_addgroupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    leader=User.query.filter(User.id==group.leaderid).first()

    # 发送消息
    id=id+1
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=send_time+", "+leader.username+"拒绝了你的申请，加入团队("+group.groupname+")失败"
    new_notice=Notice(id=id,sender_id=leader.id,receiver_id=user.id,document_id=0,
        group_id=groupid,send_time=now,content=content,type=8
    )
    db.session.add(new_notice)
    db.session.commit()
    
    response={
        'message':'success'
    }
    return jsonify(response)

# 显示该团队下的成员
# tested
@app.route('/api/get_user_bygroup/',methods=['POST'])
def get_user_bygroup():
    all_group_user=get_user_ingroup(request.form['groupid'])
    res=[]
    for user in all_group_user:
        content={
            'id':user.id,
            'username':user.username,
            'email':user.email
        }
        res.append(content)
    return jsonify(res)

# 删除团队成员
@app.route('/api/delete_user/',methods=['POST'])
def delete_user():
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    userid=request.form['userid']
    db.session.query(GroupMember).filter(and_(GroupMember.user_id==request.form['userid'],GroupMember.group_id==request.form['groupid'])).delete()
    db.session.commit()

    # 发送消息
    sender_id=request.form['leaderid']
    sender=User.query.filter(User.id==sender_id).first()
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=send_time+", "+sender.username+"将你踢出了团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=sender_id,receiver_id=userid,document_id=0,
        group_id=groupid,send_time=now,content=content,type=0
    )
    db.session.add(new_notice)
    db.session.commit()

    # 删除成员对应文档权限
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
    # 删除团队文档
    db.session.commit()
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()

    for document in all_document:
        db.session.query(DocumentUser).filter(DocumentUser.document_id==document.id).delete()
        
        db.session.commit()
    db.session.query(Document).filter(Document.group_id==groupid).delete()
    db.session.commit()
    return jsonify({'message':'success'})

####################################
########## Document操作 ###############
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
            others_modify_right=request.form['modify_right'],
            others_share_right=request.form['share_right'],
            others_discuss_right=request.form['discuss_right'],
            content=content,recycled=0,is_occupied=0,
            group_id=0,
            modified_time=0)
        db.session.add(newDocument)
        db.session.commit()

        id=get_newid()
        newDU=DocumentUser(id=id,document_id=newDocument.id,
            user_id=user.id,last_watch=0,
            favorited=0,modified_time=0,type=0)
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
            others_modify_right=request.form['others_modify_right'],
            others_share_right=request.form['others_share_right'],
            others_discuss_right=request.form['others_discuss_right'],
            content=content,recycled=0,is_occupied=0,
            group_id=group_id,modified_time=0)
        db.session.add(newDocument)
        db.session.commit()

        id=get_newid()
        i=1
        all_member=GroupMember.query.filter(GroupMember.group_id==group_id).all()
        for member in all_member:
            newDU=DocumentUser(id=id+i,document_id=newDocument.id,
            user_id=member.user_id,last_watch=0,
            favorited=0,modified_time=0,type=1)
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

# 查看我拥有的文档(除团队文档外的文档)
@app.route('/api/my_docs/',methods=['POST'])
def my_docs():
    user=User.query.filter(User.username==request.form['username']).first()
    all_du=DocumentUser.query.filter(and_(DocumentUser.user_id==user.id,DocumentUser.recycled==0)).all()
    res=[]
    for du in all_du:
        if du.recycled == 0 and du.type != 1:
            doc=Document.query.filter(du.document_id==Document.id).first()
            res.append(document_to_content(doc))
    return jsonify(res)

# 获取我创建的所有文档的信息
@app.route('/api/my_created_docs/',methods=['POST'])
def my_created_docs():
    user=User.query.filter(User.username==request.form['username']).first()
    all_document=Document.query.filter(and_(Document.creator_id==user.id,Document.recycled==0)).all()
    res=[]
    for document in all_document:
        if document.recycled == 0:
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

# 传递权限信息
@app.route('/api/tell_doc_right/',methods=['POST'])
def tell_doc_right():
    document = Document.query.filter(Document.id == request.form['DocumentID']).first()
    user=User.query.filter(User.username==request.form['username']).first()
    DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
    if(DUlink==None):
        response={
            'watch_right':False,
            'modify_right':False,
            'share_right':False,
            'discuss_right':False,
            'others_modify_right':False,
            'others_share_right':False,
            'others_discuss_right':False,
            'others_watch_right':False,
            'doctype':-1,
            'usertype':-1
        }
    elif user.id==document.creator_id:
        if document.group_id!=0:
            type=0
        else:
            type=1
        response={
            'watch_right':True,
            'modify_right':True,
            'share_right':True,
            'discuss_right':True,
            'others_modify_right':True,
            'others_share_right':True,
            'others_discuss_right':True,
            'others_watch_right':True,
            'doctype':type,
            'usertype':DUlink.type
        }
    else:
        if document.group_id!=0:
            type=0
        else:
            type=1

        modify_right=toTF(document.modify_right)
        share_right=toTF(document.share_right)
        discuss_right=toTF(document.discuss_right)
        
        others_modify_right=toTF(document.others_modify_right)
        others_share_right=toTF(document.others_share_right)
        others_discuss_right=toTF(document.others_discuss_right)
        response={
            'watch_right':True,
            'modify_right':modify_right,
            'share_right':share_right,
            'discuss_right':discuss_right,
            'others_modify_right':others_modify_right,
            'others_share_right':others_share_right,
            'others_discuss_right':others_discuss_right,
            'others_watch_right':True,
            'doctype':type,
            'usertype':DUlink.type
        }
    return jsonify(response)     

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
        # mtime=DUlink.last_watch
        # 判断用户是否有权限查看该文档
        # 初步完善
        # TODO: 目前只有创建者能查看文档(已修正)
        # TODO: 目前任何参与者都可以查看文档
        if (document!=None) and (DUlink!=None):
            msg="success"
            mcontent=document.content
            now=datetime.datetime.now()
            mtime=now
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"last_watch":now})
            db.session.commit()
            # DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        else:
            msg="fail"
            mcontent=""
    response={
        'message':msg,
        'content':mcontent,
        'time':mtime
    }
    return jsonify(response)

# 获取团队所有没有被删除的文档
@app.route('/api/get_group_docs/',methods=['POST'])
def get_group_docs():
    all_document=Document.query.filter(and_(Document.group_id==request.form['group_id'],Document.recycled==0)).all()
    res=[]
    for document in all_document:
        res.append(document_to_content(document))
    return jsonify(res)


# 修改文档
@app.route('/api/modify_doc/', methods=['POST'])
def modify_doc():
    msg=''
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        # TODO: 目前只有创建者能修改文档
        msg="success"
        now=datetime.datetime.now()
        content=request.form['content']
        db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"content":content,
            "modified_time":now
        })
        db.session.query(DocumentUser).filter(and_(DocumentUser.user_id==user.id,
            DocumentUser.document_id==request.form['DocumentID'])).update({"modified_time":now})
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 文档想要分享给其他用户前，需要先检索用户，根据用户名检索，返回所有不拥有该文档的用户
# tested
@app.route('/api/query_notindoc_user/',methods=['POST'])
def query_notindoc_user():
    keyword=request.form['keyword']
    document_id=request.form['document_id']
    res=[]
    all_user=get_user_bykeyword(keyword)
    all_document_user=get_user_indocument(document_id)
    for user in all_user:
        if user not in all_document_user:
            content={
                'id':user.id,
                'username':user.username,
                'email':user.email
            }
            res.append(content)
    return jsonify(res)

# 个人文档分享
@app.route('/api/pernal_doc_share_to/',methods=['POST'])
def personal_share_to():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.id==request.form['user_id']).first()
        target_user=User.query.filter(User.id==request.form['target_user_id']).first()
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=target_user.id,last_watch=0,
            favorited=0,type=0,modified_time=0)
        
        # 发送消息
        id=get_newid()
        now=datetime.datetime.now()
        send_time=now.strftime('%Y-%m-%d')
        content=send_time+", "+user.username+"分享给你了一个文档("+document.title+")"
        new_notice=Notice(id=id,sender_id=user.id,receiver_id=target_user.id,document_id=document.id,
            group_id=0,send_time=now,content=content,type=4
        )
        msg='success'
        db.session.add(new_notice)
        db.session.add(newDU)
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 团队文档分享
@app.route('/api/group_doc_share_to/',methods=['POST'])
def group_doc_share_to():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.id==request.form['user_id']).first()
        target_user=User.query.filter(User.id==request.form['target_user_id']).first()
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=target_user.id,last_watch=0,
            favorited=0,type=2,modified_time=0)
        
        # 发送消息
        id=get_newid()
        now=datetime.datetime.now()
        send_time=now.strftime('%Y-%m-%d')
        content=send_time+", "+user.username+"分享给你了一个文档("+document.title+")"
        new_notice=Notice(id=id,sender_id=user.id,receiver_id=target_user.id,document_id=document.id,
            group_id=0,send_time=now,content=content,type=4
        )
        msg='success'
        db.session.add(new_notice)
        db.session.add(newDU)
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 收藏文档
@app.route('/api/favor_doc/', methods=['POST'])
def favor_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        if document!=None and DUlink.favorited==0:
            msg='success'
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"favorited":1})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 取消收藏文档
@app.route('/api/cancel_favor_doc/', methods=['POST'])
def cancel_favor_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        if document!=None and DUlink.favorited==1:
            msg='success'
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"favorited":0})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 查看我收藏的文档
# 收藏的，并且没删除的
@app.route('/api/my_favor_doc/',methods=['POST'])
def my_favor_doc():
    user=User.query.filter(User.username==request.form['username']).first()
    DUlink=DocumentUser.query.filter(and_(DocumentUser.favorited==1,DocumentUser.user_id==user.id)).all()
    res=[]
    for dulink in DUlink:
        document=Document.query.filter(and_(Document.id==dulink.document_id,Document.recycled==0)).first()
        if(document):
            res.append(document_to_content(document))
    return jsonify(res)

# 修改文档基本信息
@app.route('/api/modify_doc_basic/',methods=['POST'])
def modify_doc_basic():
    db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"title":request.form['title']})
    db.session.commit()
    return sendmsg("success")

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
            db.session.query(Comment).filter(Comment.document_id==document.id).delete()
            db.session.query(Document).filter(Document.id==document.id).delete()
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 显示最近使用文档
@app.route('/api/show_recent_doc/', methods=['POST'])
def show_recent_doc():
    res=[]
    user = get_user_byusername(request.form['username'])
    all_documentuser=db.session.query(DocumentUser).filter(DocumentUser.user_id==user.id).order_by(-DocumentUser.last_watch).all()
    for DU in all_documentuser:
        document=db.session.query(Document).filter(Document.id==DU.document_id).first()
        if(document==None):
            continue
        if document.recycled == 0 :
            res.append(document_to_content(document))
    return jsonify(res)


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

# 个人文档创建者修改权限
@app.route('/api/modify_personal_doc_right/', methods=['POST'])
def modify_personal_doc_right():
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
        msg="success"
        #     "watch_right":watch_right,"modify_right":modify_right,"delete_right":delete_right,"discuss_right":discuss_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"share_right":share_right,
        #     "watch_right":watch_right,"modify_right":modify_right,"delete_right":delete_right,"discuss_right":discuss_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"watch_right":watch_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"modify_right":modify_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"delete_right":delete_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"discuss_right":discuss_right})
        db.session.commit()
        response={
            'message': msg
        }
        return jsonify(response)

# 团队文档创建者修改权限
@app.route('/api/modify_group_doc_right/', methods=['POST'])
def modify_group_doc_right():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        share_right=request.form['share_right']
        modify_right=request.form['modify_right']
        discuss_right=request.form['discuss_right']
        others_modify_right=request.form['others_modify_right'],
        others_share_right=request.form['others_share_right'],
        others_discuss_right=request.form['others_discuss_right'],
        db.session.query(Document).filter(Document.id==document.id).update({"share_right":share_right,
            "modify_right":modify_right,"discuss_right":discuss_right,
            "others_share_right":others_share_right,"others_modify_right":others_modify_right,
            "others_discuss_right":others_discuss_right})
        msg="success"
        db.session.commit()
        response={
            'message': msg
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
        document=Document.query.filter(Document.id==document_id).first()
        now=datetime.datetime.now()
        content=request.form['content']
        msg="success"
        newComment=Comment(id=id,document_id=document_id,creator_id=creator_id,content=content,created_time=now)
        db.session.add(newComment)
        db.session.commit()

        # 发送消息
        id=get_newid()
        send_time=now.strftime('%Y-%m-%d')
        content=send_time+", "+user.username+"给你的文档("+document.title+")发了一条评论"
        new_notice=Notice(id=id,sender_id=user.id,receiver_id=document.creator_id,document_id=document_id,
            group_id=0,send_time=now,content=content,type=3
        )
        db.session.add(new_notice)
        db.session.commit()

    response={
        'message': msg
    }
    return jsonify(response)

# 获取文档的所有评论
@app.route('/api/get_all_comment/', methods=['POST'])
def get_all_comment():
    all_comment=Comment.query.filter(Comment.document_id==request.form['DocumentID']).all()
    res=[]
    for comment in all_comment:
        user=User.query.filter(User.id==comment.creator_id).first()
        res.append(comment_to_content(comment,user))
    res.reverse()
    return jsonify(res)

# 获取文档所有修改记录
@app.route('/api/get_all_modified_time/',methods=['POST'])
def get_all_modified_time():
    res=[]
    all_modified_time=DocumentUser.query.filter(and_(DocumentUser.id==request.form['DocumentID'],DocumentUser.modified_time!=0)).order_by(-DocumentUser.modified_time).all()
    for tmp in all_modified_time:
        user=User.query.filter(User.id==tmp.user_id).first()
        res.append(modifiedtime_to_content(tmp,user))
    document=Document.query.filter(Document.id==request.form['DocumentID']).first()
    user=User.query.filter(User.id==document.creator_id).first()
    res.append(created_info(document,user))
    return jsonify(res)

####################################
########## 消息 操作 ###############
####################################

# 获取用户未读所有的消息
@app.route('/api/get_all_notice/',methods=['POST'])
def get_all_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(Notice.receiver_id==receiver.id).all()
    res=[]
    for notice in all_notice:
        res.append(notice_to_content(notice))
    return jsonify(res)

# 未读转已读(直接从数据库中删除)
@app.route('/api/del_new_notice/',methods=['POST'])
def del_new_notice():
    new_notice_id=request.form['new_notice_id']
    db.session.query(Notice).filter(Notice.id==new_notice_id).delete()
    db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

# 查看所有不需要确认的消息(type=0,1,3,4,5)
@app.route('/api/view_non_confirm_notice/',methods=['POST'])
def view_non_confirm_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(Notice.receiver_id==receiver.id).all()
    res=[]
    for notice in all_notice:
        stat=notice.type
        if(stat==0 or stat==1 or stat==3 or stat==4 or stat==5):
            res.append(notice_to_content(notice))
    return jsonify(res)


# 查看所有需要确认的消息(type=2) 需要有两个button，分别发出type=1、5的消息
@app.route('/api/view_confirm_notice/',methods=['POST'])
def view_confirm_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(Notice.receiver_id==receiver.id).all()
    res=[]
    for notice in all_notice:
        stat=notice.type
        if(stat==2):
            res.append(notice_to_content(notice))
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug = True)