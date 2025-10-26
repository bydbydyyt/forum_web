# Django 应用部署检查清单

## 1. 安装依赖包
```bash
pip install -r requirements.txt
```

## 2. 环境配置检查
- 确保 `DEBUG = False` 在生产环境
- 设置 `ALLOWED_HOSTS = ['your-domain.com', 'localhost', '127.0.0.1']`
- 配置正确的数据库连接

## 3. 数据库迁移
```bash
python manage.py migrate
```

## 4. 收集静态文件
```bash
python manage.py collectstatic
```

## 5. 创建超级用户（可选）
```bash
python manage.py createsuperuser
```

## 6. 生产环境特定设置
- 设置 `SECRET_KEY` 环境变量
- 配置正确的邮件设置
- 设置正确的Redis连接（用于Channels）

## 常见问题解决：

### 模板不显示元素
- 检查 `TEMPLATES` 配置中的 `DIRS` 设置
- 确保模板文件路径正确
- 运行 `collectstatic` 命令

### 静态文件404错误
- 配置Web服务器（Nginx/Apache）服务静态文件
- 或使用WhiteNoise中间件

### 数据库连接错误
- 检查数据库配置
- 确保数据库服务运行

### WebSocket连接问题
- 确保Redis服务运行
- 检查Channels配置