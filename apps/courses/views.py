from django.core.paginator import PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from django.views.generic.base import View
# Create your views here.
from pure_pagination import Paginator

from courses.models import Course
from operation.models import UserFavorite


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
        # 根据课程id获取课程记录
        course = Course.objects.get(id=int(course_id))

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