# graphene-doc-server

# 石墨烯文档

项目地址：

暂未公布。



石墨烯文档后端代码

后端代码储存在此处。

前端代码网址：
https://github.com/IAmParasite/graphene-doc-frontend

后端代码网址：

https://github.com/Coach257/graphene-doc-server



项目协作功能视频展示：

https://www.bilibili.com/video/BV1Yz4y1f7SG



# 用户手册



## 编辑界面

编辑界面分为两个区域：编辑区和左侧边栏。

![image](https://github.com/Coach257/graphene-doc-server/blob/master/READMEimage/WeChat9677db5284e153946a05948a32737e76.png)



### 左侧边栏

左侧边栏有评论、历史、分享和权限管理四个板块。

#### 评论

在评论区，可以发表对于当前文档的评论。

若是当前用户具有评论权限，则可以进行评论。

在上方文本框中键入评论内容，点击右侧的评论按钮，就可以发送评论。

已经发送的评论可以在评论区下方查看，已发表的评论按照发表时间的顺序依次排列。

![image](https://github.com/Coach257/graphene-doc-server/blob/master/READMEimage/WeChat052c99bf6178a79297ecde069dc47dc4.png)

#### 历史

创建文档和修改文档会被按照时间顺序记录。

如果当前用户对于当前文档有查看的权限，则可以查看历史记录。



#### 分享

点击分享板块可以将文档分享给站内其他用户。

如果当前用户有对于当前文档的分享权限，则可以进行分享。

![image](https://github.com/Coach257/graphene-doc-server/blob/master/READMEimage/WeChat78ed02960dc3bb7416d68164417d2391.png)



可以在搜索栏中输入部分关键字，服务器会自动返回含有关键字的用户信息，点击右侧的share按钮就可以将文档分享给他，使其获得进入文档以及相应的编辑、查看、分析等权限。

### 文档编辑区

![image](https://github.com/Coach257/graphene-doc-server/blob/master/READMEimage/WeChata6ccc1ba2a97933efeee2a489b4498f5.png)

#### 文档标题

标题区展示了文档的标题和类别。比如图中的文档标题为《文档展示》。

#### 正在编辑

正在编辑区显示了正在编辑当前文档的用户的头像。

#### 文档编辑区

文档编辑采用了[mavonEditor](https://github.com/hinesboy/mavonEditor)，支持富文本编辑和MarkDown，能够同时在文档中插入图片和文字。

**mavonEditor**是一种基于Vue的markdown编辑器。

具体文档请参见https://github.com/hinesboy/mavonEditor。

编辑区左侧为输入区，右侧为预览区。

第一行：

![image](https://github.com/Coach257/graphene-doc-server/blob/master/READMEimage/WeChata04563d836585239b22e2b862cb3448a.png)



加粗、斜体、标题、下划线、删除线、标记、上标、下标、左对齐、中对齐、右对齐、引用、标号、不可见、全屏、单窗口、双窗口



第二行：

![image](https://github.com/Coach257/graphene-doc-server/blob/master/READMEimage/WeChat862962575ae76887b4cf5e32fabb0805.png)



标号、链接、图片、代码段、表格、回撤、重做、删除、保存

