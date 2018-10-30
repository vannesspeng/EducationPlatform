#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:pyy
# datetime:2018/10/10 15:01
# encoding: utf-8
import xadmin
from .models import Course, Lesson, Video, CourseResource, BannerCourse


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                    'add_time']  # 一次显示你想出现的多行数据
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image',
                     'click_nums']  # 查询你想要的数据
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                   'add_time']  # 过滤器

    # 默认排序：以点击数排序
    #ordering = ['-click_nums']

    # 字段只读：点击数只允许读取
    #readonly_fields = ['click_nums', 'fav_nums']

    # 字段隐藏：收藏数隐藏显示
    #exclude = ['fav_nums']

    # 课程直接添加章节,课程资源
    inlines = [LessonInline, CourseResourceInline]

    # 直接列表页编辑
    list_editable = ['degree', 'desc', ]

    refresh_times = [3, 5]  # 列表页定时刷新3s或者5s
    # 字段显示样式
    style_fields = {"detail": "ueditor"}

    import_excel = True

    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    # 字段联动
    def save_models(self):
        # 在保存课程的时候,统计课程机构的课程数
        obj = self.new_obj
        # 新增课程还没有保存，统计的课程数就会少一个
        obj.save()
        # 必须确定存在
        if obj.course_org is not None:
            # obj实际是一个course对象
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                    'add_time']  # 一次显示你想出现的多行数据
    search_fields = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image',
                     'click_nums']  # 查询你想要的数据
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'fav_nums', 'image', 'click_nums',
                   'add_time']  # 过滤器

    # 课程直接添加章节,课程资源
    inlines = [LessonInline, CourseResourceInline]

    # 过滤列表中的数据
    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs

class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course__name', 'name']

    # __name代表使用外键中name字段
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson__name', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course__name', 'name', 'download']
    # __name代表使用外键中name字段
    list_filter = ['course__name', 'name', 'download', 'add_time']


# 将管理器与model进行注册关联
xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
