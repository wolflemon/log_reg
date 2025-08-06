"""
URL configuration for auth_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.users import views  # 导入视图函数
from django.conf import settings  
from django.conf.urls.static import static  
from allauth.account import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.home_view, name='home'),  # 使用视图函数
    path('users/', include('apps.users.urls')),

    #以下四条移植而来
    path('neo4j-data/', get_neo4j_data, name='neo4j_data'),  # 获取neo4j的节点和边信息 ?searchTerm=... 表示只获取相关节点和边的信息
    path('click-node/', click_node), # 点击图谱节点展示课程信息
    path('accounts/password_change/',
         account_views.PasswordChangeView.as_view(),
         name='account_change_password'), # 原accounts/password/change路径深度造成static文件获取错误
    path('', home_view, name='home'),  # 首页（图谱）
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)