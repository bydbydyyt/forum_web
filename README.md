# 论坛与私聊系统

这是一个基于Django开发的现代化论坛和私聊系统。

## 主要功能

- 论坛功能
  - 分区发帖
  - 支持文字、图片、视频内容
  - 点赞和收藏功能
  - 热度排行榜
  - 违禁词过滤
  
- 私聊功能
  - 好友系统
  - 实时聊天
  - 文件传输
  - 图片视频分享

- 用户系统
  - 个人主页
  - 自定义背景
  - 个人简介
  - 好友代码系统
  - 收藏夹管理

## 技术栈

- 后端：Django 5.0
- 前端：Bootstrap 5
- 实时通信：Django Channels
- 数据库：SQLite（开发）/ PostgreSQL（生产）
- 文件存储：本地存储

## 安装说明

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 数据库迁移：
```bash
python manage.py migrate
```

4. 创建超级用户：
```bash
python manage.py createsuperuser
```

5. 运行开发服务器：
```bash
python manage.py runserver
```

## 项目结构

```
forum_web/
├── forum/          # 论坛应用
├── chat/           # 私聊应用
├── users/          # 用户系统
├── static/         # 静态文件
├── templates/      # 模板文件
└── media/          # 用户上传文件
``` 