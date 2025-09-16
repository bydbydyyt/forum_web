1.首先打开WSL启动Redis(sudo service redis-server start)(redis-cli ping)
2.启动daphne(daphne -b 0.0.0.0 -p 8000 forum_web.asgi:application)
3.打开网站