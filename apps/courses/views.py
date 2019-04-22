from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
# Create your views here.
from pure_pagination import Paginator

from courses.models import Course, Video, CourseResource
from operation.models import UserFavorite, CourseComments, UserCourse


class CourseListView(View):
    def get(self, request):
        all_course = Course.objects.all()
        # 热门课程推荐
        hot_courses = Course.objects.all().order_by("-students")[:3]
        # 获取搜索关键字
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_course = all_course.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) |
                                           Q(detail__icontains=search_keywords))

        # 获取sort参数
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_course = all_course.order_by('-students')
            elif sort == 'hot':
                all_course = all_course.order_by('-click_nums')
        # 获取页码page
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_course, 6, request=request)
        all_course = p.page(page)
        return render(request, 'course-list.html', {
            'all_course': all_course,
            'sort': sort,
            'hot_courses': hot_courses,
            'search_keywords': search_keywords
        })


class CourseDetailView(View):
    def get(self, request, course_id):
        # 根据课程id获取课程记录,添加课程点击数
        course = Course.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        #相关课程推荐，相关的课程就是TAG相同的课程
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag).exclude(id=course_id)
        else:
            relate_courses = []

        #两个参数判断课程详情页面的收藏按钮的显示状态
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_type=1, fav_id=course.id):
                #说明课程已收藏
                has_fav_course = True

            if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=course.course_org.id):
                has_fav_org = True

        if course:
            return render(request, 'course-detail.html', {
                'course': course,
                "has_fav_course": has_fav_course,
                "has_fav_org": has_fav_org,
                "relate_courses": relate_courses
            })

class CourseInfoView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        # 此处的id为表默认为我们添加的值。
        course = Course.objects.get(id=int(course_id))
        # 查询用户是否开始学习了该课，如果还未学习则，加入用户课程表
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            course.students += 1
            course.save()
            user_course.save()
        # 查询课程资源
        all_resources = CourseResource.objects.filter(course=course)
        # 选出学了这门课的学生关系
        user_courses = UserCourse.objects.filter(course=course)

        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course_id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by("-click_nums").exclude(id=course_id)
        return render(request, 'course-video.html', {
            'course': course,
            "all_resources": all_resources,
            'relate_courses': relate_courses,
        })

class CommentsView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=course_id)
        all_comments = CourseComments.objects.filter(course_id=course_id)
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).exclude(id=course_id)
        return render(request, 'course-comment.html', {
            'course': course,
            "all_comments": all_comments,
            'relate_courses': relate_courses
        })

class AddCommentsView(View):
    def post(self, request):
        #1、判断用户是否登录
        if not request.user.is_authenticated:
            return HttpResponse('{"status":"fail","msg":"用户未登录" }', content_type="application/json")

        # 2、获取course_id和评论内容
        course_id = request.POST.get("course_id", "")
        comments = request.POST.get("comments", "")

        if int(course_id) > 0 and comments:
            course = Course.objects.get(id=course_id)
            course_comment = CourseComments()
            course_comment.course = course
            course_comment.comments = comments
            course_comment.user = request.user
            course_comment.save()
            return HttpResponse('{"status":"success","msg":"评论成功！"}', content_type="application/json")
        else:
            return HttpResponse('{"status":"fail", "msg":"评论失败！请重新尝试!"}', content_type="application/json")



class VideoPlayView(View):
    def get(self,request, video_id):
        video = Video.objects.get(id=video_id)
        course = video.lesson.course
        # 查询一下该用户是否学习了该课程，如果没有则需要添加
        user_course = UserCourse.objects.filter(user=request.user, course_id=course.id)
        if not user_course:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        #查询课程资源
        all_resources = CourseResource.objects.filter(course=course)
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user_id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).exclude(id=course.id)

        return render(request, 'course-play.html', {
            "video": video,
            "course": course,
            "all_resources": all_resources,
            "relate_courses":relate_courses
        })