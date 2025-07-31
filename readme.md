# 访问测试

Admin 后台：http://127.0.0.1:8000/admin（使用超级用户登录）

登录页面：http://127.0.0.1:8000/accounts/login/

注册页面：http://127.0.0.1:8000/accounts/signup/

首页：http://127.0.0.1:8000/

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