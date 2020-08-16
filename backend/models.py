from functools import wraps
from flask import Flask, flash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_,not_
import config
app = Flask(__name__)
app.config.from_object(config)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__='User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    description=db.Column(db.TEXT)

    def __repr__(self):
        return "<User %r>" % self.username
        
class Group(db.Model):
    __tablename__='Group'
    id=db.Column(db.Integer,primary_key=True)
    groupname=db.Column(db.String(255))
    leaderid=db.Column(db.Integer)
    createdtime=db.Column(db.DateTime)
    description=db.Column(db.String(255))
    
    def __repr__(self):
        return "<Group %r>" % self.groupname

class GroupMember(db.Model):
    __tablename__='GroupMember'
    id=db.Column(db.Integer,primary_key=True)
    group_id=db.Column(db.Integer)
    user_id=db.Column(db.Integer)

    def __repr__(self):
        return "<GroupMember %r>" %self.id

class Document(db.Model):
    __tablename__='Document'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    creator_id=db.Column(db.Integer)
    created_time=db.Column(db.DateTime)
    modified_time=db.Column(db.DateTime)
    content=db.Column(db.TEXT)

    modify_right=db.Column(db.Integer)
    share_right=db.Column(db.Integer)
    discuss_right=db.Column(db.Integer)
    
    others_modify_right=db.Column(db.Integer)
    others_share_right=db.Column(db.Integer)
    others_discuss_right=db.Column(db.Integer)   
    
    recycled=db.Column(db.Integer)
    is_occupied=db.Column(db.Integer) # 0: Not occupied, 1: Occupied
    group_id=db.Column(db.Integer) # 0: Personal document, not 0: Group document
    def __repr__(self):
        return "<Document %r>" % self.title


class DocumentUser(db.Model):
    __tablename__='DocumentUser'
    id=db.Column(db.Integer, primary_key=True)
    document_id=db.Column(db.Integer)
    user_id=db.Column(db.Integer)
    # is_creator=db.Column(db.Boolean)
    # share_right=db.Column(db.Integer)
    # watch_right=db.Column(db.Integer)
    # modify_right=db.Column(db.Integer)
    # delete_right=db.Column(db.Integer)
    # discuss_right=db.Column(db.Integer)
    last_watch=db.Column(db.DateTime)
    favorited=db.Column(db.Integer)
    modified_time=db.Column(db.DateTime)
    # recycled=db.Column(db.Integer)
    type=db.Column(db.Integer) # 0: personal 1: group 2: 被分享的团队文档

    def __repr__(self):
        return "<DocumentUser %r>" % self.document_user_id

class Comment(db.Model):
    __tablename__='Comment'
    id=db.Column(db.Integer,primary_key=True)
    document_id=db.Column(db.Integer)
    creator_id=db.Column(db.Integer)
    content=db.Column(db.TEXT)
    created_time=db.Column(db.DateTime)

class Notice(db.Model):
    __tablename__='Notice'
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.String(255))
    receiver_id=db.Column(db.String(255))
    document_id=db.Column(db.Integer)
    group_id=db.Column(db.Integer)
    send_time=db.Column(db.DateTime)
    content=db.Column(db.TEXT)
    type=db.Column(db.Integer)
# type:
# 0:我被踢出团队 传content、group_id "a将你踢出了团队xxx"
# 1:我被邀请加入某个团队，我选择接受加入团队 传group_id、content 发送给sender "a通过了你的邀请"
# 2:我邀请他人加入某个团队，对方通过/拒绝 传group_id、content 发送给receiver "a邀请你加入团队xxx"
# 3:我创建的文档被评论 评论者传给创建者 document_id、content 发送 "你的文档xxx被a评论"
# 4:收到了来自他人分享来的文件，传document_id、content 由sender发送 "你收到了来自a分享的文档xxx"
# 5:我被邀请加入某个团队，我选择拒绝加入团队 传group_id、content 发送给sender "a拒绝了你的邀请"