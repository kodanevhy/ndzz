# _*_ encoding:utf-8 _*_

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin

from pure_pagination import Paginator, PageNotAnInteger

from .models import CourseOrg, CityDict, Teacher
from operation.models import UserFavorite
from courses.models import Courses
from .forms import UserAskForm

# Create your views here.


class OrgView(View):
    """
    课程机构列表功能
    """
    def get(self, request):
        # 课程机构
        all_orgs = CourseOrg.objects.all()
        hot_orgs = all_orgs.order_by("-click_nums")[:3]
        # 城市
        all_citys = CityDict.objects.all()

        # 取出筛选城市
        city_id = request.GET.get('city', "")
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选
        category = request.GET.get('ct', "")
        if category:
            all_orgs = all_orgs.filter(category=category)

        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        org_nums = all_orgs.count()

        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 5, request=request)

        orgs = p.page(page)
        return render(request, "org-list.html", {
            "all_orgs": orgs,
            "all_citys": all_citys,
            "org_nums": org_nums,
            "city_id": city_id,
            "category": category,
            "hot_orgs": hot_orgs,
            "sort": sort,
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            userask_form.save(commit=True)
            json_success_data = {'status': 'success'}
            return HttpResponse(json.dumps(json_success_data),
                                content_type="application/json")
        else:
            json_fail_data = {'status': 'fail', 'msg': u'添加出错'}
            return HttpResponse(json.dumps(json_fail_data),
                                content_type="application/json")


class OrgHomeView(View):
    """
    机构首页
    """
    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        course_org = CourseOrg.objects.get(id=int(org_id))
        all_courses = course_org.courses_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]
        return render(request, 'org-detail-homepage.html', {
            "all_courses": all_courses,
            "all_teachers": all_teachers,
            "course_org": course_org,
            "current_page": current_page,
            'has_fav': has_fav,
        })


class OrgCourseView(View):
    """
    机构课程列表页
    """
    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.courses_set.all()[:3]
        return render(request, 'org-detail-course.html', {
            "all_courses": all_courses,
            "course_org": course_org,
            "current_page": current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    """
    机构介绍页
    """
    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            "course_org": course_org,
            "current_page": current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    """
    机构教师页
    """
    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teachers = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            "all_teachers": all_teachers,
            "course_org": course_org,
            "current_page": current_page,
            'has_fav': has_fav,
        })


class AddFavView(View):
    """
    用户收藏，用户取消收藏
    """
    def post(self, request):
        # fav_id和fav_type是org_base.html中Ajax传入的
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        # 判断用户登录状态
        if not request.user.is_authenticated():
            json_fail_data_notlogin = {'status': 'fail', 'msg': '用户未登录'}
            return HttpResponse(json.dumps(json_fail_data_notlogin),
                                content_type="application/json")

        exist_records = UserFavorite.objects.filter(user=request.user,
                                    fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 如果记录已经存在，则表示用户取消收藏
            exist_records.delete()
            if int(fav_type) == 1:
                course = Courses.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()

            json_success_data_cancelfav = {'status': 'success', 'msg': '收藏'}
            return HttpResponse(json.dumps(json_success_data_cancelfav), content_type="application/json")
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()
                if int(fav_type) == 1:
                    course = Courses.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()
                json_success_data = {'status': 'success', 'msg': '已收藏'}
                return HttpResponse(json.dumps(json_success_data), content_type="application/json")
            else:
                json_fail_data_error = {'status': 'fail', 'msg': '收藏出错'}
                return HttpResponse(json.dumps(json_fail_data_error), content_type="application/json")


class TeacherListView(View):
    """
    课程讲师列表页
    """
    def get(self, request):
        all_teachers = Teacher.objects.all()

        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")

        # 讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]

        teacher_nums = all_teachers.count()

        # 对讲师进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, 5, request=request)

        teachers = p.page(page)
        return render(request, "teachers-list.html", {
            "all_teachers": teachers,
            "sort": sort,
            "sorted_teacher": sorted_teacher,
            "teacher_nums": teacher_nums,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums += 1
        teacher.save()
        all_courses = Courses.objects.filter(teacher=teacher)
        has_teacher_faved = False
        has_org_faved = False
        if request.user.is_authenticated():

            if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=int(teacher.id)):
                has_teacher_faved = True

            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=int(teacher.org.id)):
                has_org_faved = True

        # 讲师排行
        sorted_teacher = Teacher.objects.all().order_by("-click_nums")[:3]
        return render(request, "teacher-detail.html",{
            "teacher": teacher,
            "all_courses": all_courses,
            "sorted_teacher": sorted_teacher,
            "has_teacher_faved": has_teacher_faved,
            "has_org_faved": has_org_faved,
        })