#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/12 16:09
# @Author  : Yormng
# @Site    :
# @File    : urls.py
# @Software: PyCharm

from django.conf.urls import url

from views import UserInfoView, UploadImageView, UpdatePwdView, MyCourseView, MyFavOrgView, MyFavTeacherView, \
    MyFavCourseView, MyMessageView

urlpatterns = [
    # 用户信息
    url(r'^info/$', UserInfoView.as_view(), name="user_info"),
    # 用户头像上传
    url(r'^image/upload/$', UploadImageView.as_view(), name="image_upload"),
    # 用户个人中心修改密码
    url(r'update/pwd/$', UpdatePwdView.as_view(), name="update_pwd"),
    # 我的课程
    url(r'^mycourse', MyCourseView.as_view(), name="mycourse"),
    # 我收藏的课程机构
    url(r'^myfav/org/$', MyFavOrgView.as_view(), name="myfav_org"),
    # 我收藏的授课教师
    url(r'^myfav/teacher/$', MyFavTeacherView.as_view(), name="myfav_teacher"),
    # 我收藏的课程
    url(r'^myfav/course/$', MyFavCourseView.as_view(), name="myfav_course"),
    # 我的个人中心消息
    url(r'mymessage/$', MyMessageView.as_view(), name="mymessage")
]