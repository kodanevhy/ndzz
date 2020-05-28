#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/5 0:35
# @Author  : Yormng
# @Site    : 
# @File    : adminx.py
# @Software: PyCharm

import xadmin
# 为了注册网站的一些全局设置（BaseSetting, GlobalSetting等）而导入
from xadmin import views

from .models import EmailVerifyRecord, Banner


class BaseSetting(object):
    # 开启主题功能
    enable_themes = True
    # 开启主题的种类可供选择
    use_bootswatch = True


class GlobalSetting(object):
    # 修改网站的logo标识
    site_title = "同而知后台管理系统"
    # 修改网站底部标识
    site_footer = "同而知在线网"
    # 收起菜单栏
    menu_style = "accordion"


class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
# 注册BaseSetting（区别于模型的注册）
xadmin.site.register(views.BaseAdminView, BaseSetting)
# 注册GlobalSetting（区别于模型的注册）
xadmin.site.register(views.CommAdminView, GlobalSetting)




