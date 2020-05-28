#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/4/5 14:36
# @Author  : Yormng
# @Site    : 
# @File    : email_send.py
# @Software: PyCharm

from random import Random
# 发送邮件专用
from django.core.mail import send_mail

from users.models import EmailVerifyRecord
from ndzz.settings import EMAIL_FROM


# 生成邮箱验证码
def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    # (0, length)中的任何一个，共取8个。
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


# 将获取到的邮箱（用户名）拿到这里来
def send_register_email(email, send_type="register"):
    # 将发送给用户的验证码(code)事先保存到数据库中
    email_record = EmailVerifyRecord()
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "同而知在线网注册激活链接"
        email_body = "请点击下方的链接激活你的账号：http://127.0.0.1:8000/active/{0}".format(code)

        # 发送邮件，[email]指将邮箱发送给谁
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass

    elif send_type == "forget":
        email_title = "同而知在线网密码重置链接"
        email_body = "请点击下方的链接重置你的密码：http://127.0.0.1:8000/reset/{0}".format(code)

        # 发送邮件，[email]指将邮箱发送给谁
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
