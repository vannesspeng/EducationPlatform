from django.core.paginator import PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from django.views.generic.base import View
# Create your views here.
from pure_pagination import Paginator

from courses.models import Course


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
