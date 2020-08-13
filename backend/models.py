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
    modify_right=db.Column(db.Integer)
    share_right=db.Column(db.Integer)
    discuss_right=db.Column(db.Integer)
    content=db.Column(db.TEXT)
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
    share_right=db.Column(db.Integer)
    watch_right=db.Column(db.Integer)
    modify_right=db.Column(db.Integer)
    delete_right=db.Column(db.Integer)
    discuss_right=db.Column(db.Integer)
    def __repr__(self):
        return "<DocumentUser %r>" % self.document_user_id

class Comment(db.Model):
    __tablename__='Comment'
    id=db.Column(db.Integer,primary_key=True)
    document_id=db.Column(db.Integer)
    creator_id=db.Column(db.Integer)
    content=db.Column(db.TEXT)
    created_time=db.Column(db.DateTime)