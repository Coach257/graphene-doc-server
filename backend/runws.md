cd graphene-doc/websocket 进入项目目录
source env/bin/activate 激活虚拟环境
python websocket.py 运行程序
deactivate 退出虚拟环境


启动服务器流程：
cd /root/graphene-doc/backend   绝对路径进入文件夹
source env/bin/activate         启动虚拟环境
export PATH=$PATH:/usr/local/python3.7/bin  设置环境变量
gunicorn -w 4 -b 127.1.0.0:8080 app:app     多线程启动
gunicorn -w 1 -b 127.1.0.0:8080 app:app 
gunicorn -w 1 -b 172.17.0.17:8080 app:app   
gunicorn -w 4 -b 172.17.0.17:8080 app:app –timeout 120

查看nginx是否运行：
cd /etc/nginx/sites-available/      绝对路径进入文件夹
netstat -lnp|grep 5000              查看端口占用情况 80 8081
ps -ef | grep nginx                 查看nginx是否运行
nginx -s reload                     重新加载nginx 
service nginx restart               重启服务