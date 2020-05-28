# _*_ coding: utf-8 _*_
from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
import json

from pure_pagination import Paginator, PageNotAnInteger

from courses.models import Courses
from .models import Courses, CourseResource
from operation.models import UserFavorite, CourseComments

# Create your views here.


class CourseListView(View):
    """
    课程列表页
    """

    def get(self, request):
        all_courses = Courses.objects.all().order_by("-add_time")

        hot_courses = Courses.objects.all().order_by("-click_nums")[:3]

        # 课程排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_courses = all_courses.order_by("-click_nums")
            elif sort == "students":
                all_courses = all_courses.order_by("-students")

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_courses, 6, request=request)

        courses = p.page(page)

        return render(request, 'course-list.html', {
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses,
        })


class CourseDetailView(View):
    """
    课程详情页
    """

    def get(self, request, course_id):
        course = Courses.objects.get(id=int(course_id))
        # 增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        tag = course.tag
        if tag:
            relate_courses = Courses.objects.filter(tag=tag)[:1]

        else:
            relate_courses = []

        return render(request, "course-detail.html", {
            "course": course,
            "relate_courses": relate_courses,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
        })


class CourseInfoView(View):

    def get(self, request, course_id):
        course = Courses.objects.get(id=int(course_id))
        course.students += 1
        course.save()
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "course_resources": all_resources,
        })


class CommentView(View):

    def get(self, request, course_id):
        course = Courses.objects.get(id=int(course_id))
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all()
        return render(request, "course-comment.html", {
            "course": course,
            "course_resources": all_resources,
            "all_comments": all_comments,
        })


class AddCommentsView(View):
    """
    用户添加课程评论
    """
    def post(self, request):
        # 判断用户登录状态
        if not request.user.is_authenticated():
            json_fail_data_notlogin = {'status': 'fail', 'msg': '用户未登录'}
            return HttpResponse(json.dumps(json_fail_data_notlogin), content_type="application/json")

        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        if course_id > 0 and comments:
            course_comments = CourseComments()
            course = Courses.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            json_success_add_data = {'status': 'success', 'msg': '添加成功'}
            return HttpResponse(json.dumps(json_success_add_data), content_type="application/json")
        else:
            json_fail_add_data = {'status': 'success', 'msg': '添加失败'}
            return HttpResponse(json.dumps(json_fail_add_data), content_type="application/json")
