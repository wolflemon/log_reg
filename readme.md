# 访问测试

Admin 后台：http://127.0.0.1:8000/admin（使用超级用户登录）

登录页面：http://127.0.0.1:8000/accounts/login/

注册页面：http://127.0.0.1:8000/accounts/signup/

首页：http://127.0.0.1:8000/
本地激活虚拟环境
.\venv\Scripts\Activate.ps1
服务器激活虚拟环境（命令行前显示(venv)）
source venv/bin/activate
验证激活成功
which python  # 应显示/opt/course-recommendation-platform/venv/bin/python

- 启动服务器（不要按Ctrl+C）
python manage.py runserver 0.0.0.0:8000

http://你的服务器IP:8000/accounts/signup/
我们的服务器IP：106.52.220.222
即：
注册页面：http://106.52.220.222:8000/accounts/signup/

- 生产环境下，80端口，启动并设置开机自启
http://106.52.220.222/ 可24h访问,而8000端口只有在开发服务器运行时才可以访问
重新加载systemd配置
sudo systemctl daemon-reload

启动服务
sudo systemctl start course-platform

设置开机自启
sudo systemctl enable course-platform

验证状态（应显示active running）
sudo systemctl status course-platform

# 复制应用到现有项目
cp -r colleague_project/backend/apps/new_app /opt/course-recommendation-platform/apps/

# 添加到INSTALLED_APPS（settings.py）
INSTALLED_APPS = [
    # ...现有应用...
    'apps.new_app',  # 添加新应用
]

# 合并URL路由（config/urls.py）
urlpatterns = [
    # ...现有路由...
    path('new_app/', include('apps.new_app.urls')),  # 添加新应用路由
]

进行ettings.py同目录下文件的迁移 1/1
复制templates文件夹中内容 1/1
复制static文件夹中的内容 1/1

数据库连接：bolt://localhost:7687（你的 Python 代码已配置）
网页管理：访问 http://localhost:7474（使用密码123456789登录）

子节点统计逻辑写了，明天再改改推荐图谱界面，提交一次。