#!/usr/bin/python3
# -*- coding: utf8 -*-
from flask import Flask,request
import json
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from geventwebsocket.websocket import WebSocket   #这条做语法提示用

app = Flask(__name__)

users = set()
@app.route('/conn')
def index():
    wsock = request.environ.get('wsgi.websocket')
    users.add(wsock)
    while True:
        message = wsock.receive()
        print(message)
        if message:
            for user in users:
                if user!=wsock:
                    try:
                        user.send(message)
                    except:
                        print("用户断开连接") 
                        users.remove(wsock)



if __name__ == '__main__':
    # app.run()
    #在APP外封装websocket
    http_serv = WSGIServer(("127.0.0.1",8888),app,handler_class=WebSocketHandler)
    # 启动服务
    http_serv.serve_forever()