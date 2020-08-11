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
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return "<User %r>" % self.username
        
class Group(db.Model):
    __tablename__='Group'
    id=db.Column(db.Integer,primary_key=True)
    groupname=db.Column(db.String(80))
    leaderid=db.Column(db.Integer)
    createdtime=db.Column(db.DateTime)
    description=db.Column(db.String(80))
    
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
    title = db.Column(db.String(80), unique=True)
    creator_id=db.Column(db.Integer)
    created_time=db.Column(db.DateTime)
    content=db.Column(db.String(100000005))
    def __repr__(self):
        return "<Document %r>" % self.title

class DocumentUser(db.Model):
    __tablename__='DocumentUser'
    DocumentUserID=db.Column(db.Integer, primary_key=True)
    DocumentID=db.Column(db.Integer)
    UserID=db.Column(db.Integer)
    IsCreator=db.Column(db.Boolean)
    ShareRight=db.Column(db.Boolean)
    WatchRight=db.Column(db.Boolean)
    ModifyRight=db.Column(db.Boolean)
    DiscussRight=db.Column(db.Boolean)
    def __repr__(self):
        return "<DocumentUser %r>" % self.DocumentUserID