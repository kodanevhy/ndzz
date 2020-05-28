# _*_ coding: utf-8 _*_
from django.shortcuts import render
# 用户登录必备
from django.contrib.auth import authenticate, login, logout
# 判断用户名密码是否正确所需的父类中的authenticate方法
from django.contrib.auth.backends import ModelBackend
from django.views.generic import View
from django.db.models import Q
# 对密码加密存进数据库
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
import json
from pure_pagination import Paginator, PageNotAnInteger
from django.core.urlresolvers import reverse

from .models import UserProfile, EmailVerifyRecord
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_register_email
from django.contrib.auth.mixins import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Courses
from users.models import Banner


# 可以使用用户名或邮箱登录
class CustomBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        try:

            user = UserProfile.objects.get(Q(email=username) | Q(username=username))
            # 单独判断密码
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html", {})


class RegisterViewer(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            # 将用户注册的用户名、密码存入数据库，密码加密存储。
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户已经存在"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            # 由于默认是True，但由于实际还未激活，应该写激活的逻辑代码
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册“同而知”在线网"
            user_message.save()

            send_register_email(user_name, "register")
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


class LogoutView(View):
    """
    用户退出登录
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        # 判断用户输入是否符合表单
        if login_form.is_valid():
            # 获取用户名和密码
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            # 将获取到的用户名密码和已存在的用户名密码比对；如果传过来的是邮箱则调用ModelBackend
            user = authenticate(username=user_name, password=pass_word)
            # 判断是否已经取到了用户名和密码
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg": "用户未激活"})
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form": forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            send_register_email(email, "forget")
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})


class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email": email})
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html", {})


class ModifyPwdView(View):
    """
    修改用户密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html",
                              {"email": email, "msg": "密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, "login.html")

        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html",
                          {"email": email, "modify_form": modify_form})


class UserInfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        current_page = "info"
        return render(request, "usercenter-info.html", {
            "current_page": current_page,
        })

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            json_success_data = {'status': 'success'}
            return HttpResponse(json.dumps(json_success_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type="application/json")


class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            json_success_data = {'status': 'success'}
            return HttpResponse(json.dumps(json_success_data), content_type="application/json")
        else:
            json_fail_data = {'status': 'fail'}
            return HttpResponse(json.dumps(json_fail_data), content_type="application/json")


class UpdatePwdView(View):
    """
    个人中心修改用户密码
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                json_fail_data = {'status': 'fail', 'msg': '密码不一致'}
                return HttpResponse(json.dumps(json_fail_data), content_type="application/json")
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            json_success_data = {'status': 'success'}
            return HttpResponse(json.dumps(json_success_data), content_type="application/json")

        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type="application/json")


class MyCourseView(View, LoginRequiredMixin):
    """
    我的课程
    """
    def get(self, request):
        current_page = "course"
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {
            "user_courses": user_courses,
            "current_page": current_page,
        })


class MyFavOrgView(View, LoginRequiredMixin):
    """
    我收藏的课程
    """
    def get(self, request):
        current_page = "myfav"
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {
            "org_list": org_list,
            "current_page": current_page,
        })


class MyFavTeacherView(View, LoginRequiredMixin):
    """
    我收藏的授课教师
    """
    def get(self, request):
        current_page = "myfav"
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {
            "teacher_list": teacher_list,
            "current_page": current_page,
        })


class MyFavCourseView(View, LoginRequiredMixin):
    """
    我收藏的课程
    """
    def get(self, request):
        current_page = "myfav"
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Courses.objects.get(id=course_id)
            course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {
            "course_list": course_list,
            "current_page": current_page,
        })


class MyMessageView(View, LoginRequiredMixin):
    """
    我的个人中心消息
    """
    def get(self, request):
        current_page = "message"
        all_messages = UserMessage.objects.filter(user=int(request.user.id))

        # 对个人消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_messages, 5, request=request)

        all_messages = p.page(page)
        return render(request, 'usercenter-message.html', {
            "all_messages": all_messages,
            "current_page": current_page,
        })


class IndexView(View):
    """
    首页
    """
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        # 取出课程
        courses = Courses.objects.all()[:4]
        # 取出课程机构
        course_orgs = CourseOrg.objects.all()[:10]
        return render(request, 'index.html', {
            "all_banners": all_banners,
            "courses": courses,
            "course_orgs": course_orgs,
        })


def page_not_found(request):
    # 全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response


def page_forbidden(request):
    # 全局403处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('403.html', {})
    response.status_code = 403
    return response
