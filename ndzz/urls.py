# _*_ coding: utf-8 _*_
"""ndzz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# 该类的作用是：无需写后台的view就可以返回对应的页面
from django.views.generic import TemplateView

import xadmin
from django.views.static import serve

from users.views import LoginView, RegisterViewer, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView,\
    IndexView

from ndzz.settings import MEDIA_ROOT
# from ndzz.settings import STATIC_ROOT

urlpatterns = [
    url(r'^admin/', xadmin.site.urls),

    url('^$', IndexView.as_view(), name="index"),
    url(r'^accounts/login', TemplateView.as_view(template_name="login.html"), name="login_accounts_login"),
    url('^login/$', LoginView.as_view(), name="login"),
    url('^logout/$', LogoutView.as_view(), name='logout'),

    url('^register/$', RegisterViewer.as_view(), name="register"),

    url(r'^captcha/', include('captcha.urls')),

    # 利用正则表达式将active后面的所有内容保存到active_code变量中，用于激活用户
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),

    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),

    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset_pwd"),

    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),

    # 课程机构url配置
    url(r'^org/', include('organization.urls', namespace="org")),

    # 配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    # 当settings文件中debug=true时，这里要注释（还有settings文件中的STATIC_ROOT也要注释）
    # url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),

    # 课程相关url配置
    url(r'^course/', include('courses.urls', namespace="course")),

    url(r'^users/', include('users.urls', namespace="users")),

]

# 全局404页面配置
handler404 = 'users.views.page_not_found'
# 全局500页面配置
handler500 = 'users.views.page_error'
# 全局403页面配置
handler403 = 'users.views.page_forbidden'
