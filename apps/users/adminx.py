#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:pyy
# datetime:2018/10/10 10:01
from django.contrib.auth.models import Group, Permission

import xadmin
from courses.models import Course, Lesson, Video, CourseResource, BannerCourse
from operation.models import CourseComments, UserCourse, UserFavorite, UserMessage, UserAsk
from organization.models import CityDict, Teacher, CourseOrg
from xadmin import views
from xadmin.models import Log

from .models import EmailVerifyRecord, Banner, UserProfile


# 创建admin的管理类，不再是集成admin，而是集成object
class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    # 配置搜索字段,不做时间搜索
    search_fields = ['code', 'email', 'send_type']
    # 配置筛选字段
    list_filter = ['code', 'email', 'send_type', 'send_time']
    model_icon = 'fa fa-envelope'


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


# X admin的全局配置信息设置
class BaseSetting(object):
    # 主题功能开启
    enable_themes = True
    use_bootswatch = True


class GlobalSettings(object):
    site_title = "i爱习后台管理"
    site_footer = "isdutynet.top"
    # 收起菜单
    menu_style = "accordion"

    def get_site_menu(self):
        return (
            {
                'title': '课程管理',
                'icon': 'fa fa-book',
                'menus': (
                    {'title': '普通课程', 'icon': 'fa fa-info', 'url': self.get_model_url(Course, 'changelist')},
                    {'title': '轮播课程', 'icon': 'fa fa-info', 'url': self.get_model_url(BannerCourse, 'changelist')},
                    {'title': '章节信息', 'icon': 'fa fa-puzzle-piece', 'url': self.get_model_url(Lesson, 'changelist')},
                    {'title': '视频信息', 'icon': 'fa fa-play-circle', 'url': self.get_model_url(Video, 'changelist')},
                    {'title': '课程资源', 'icon': 'fa fa-files-o', 'url': self.get_model_url(CourseResource, 'changelist')},
                    {'title': '课程评论', 'icon': 'fa fa-comment', 'url': self.get_model_url(CourseComments, 'changelist')},
                ),
            },
            {
                'title': '机构管理',
                'icon': 'fa fa-sitemap',
                'menus': (
                    {'title': '所在城市', 'icon': 'fa fa-map-marker', 'url': self.get_model_url(CityDict, 'changelist')},
                    {'title': '机构讲师', 'icon': 'fa fa-user', 'url': self.get_model_url(Teacher, 'changelist')},
                    {'title': '机构信息', 'icon': 'fa fa-info', 'url': self.get_model_url(CourseOrg, 'changelist')},
                )},
            {
                'title': '用户管理',
                'icon': 'fa fa-user',
                'menus': (
                    {'title': '用户信息', 'icon': 'fa fa-info', 'url': self.get_model_url(UserProfile, 'changelist')},
                    {'title': '邮箱验证', 'icon': 'fa fa-envelope', 'url': self.get_model_url(EmailVerifyRecord, 'changelist')},
                    {'title': '用户课程', 'icon': 'fa fa-book', 'url': self.get_model_url(UserCourse, 'changelist')},
                    {'title': '用户收藏', 'icon': 'fa fa-star', 'url': self.get_model_url(UserFavorite, 'changelist')},
                    {'title': '用户消息', 'icon': 'fa fa-comment', 'url': self.get_model_url(UserMessage, 'changelist')},
                )},
            {
                'title': '系统管理',
                'icon': 'fa fa-cogs',
                'menus': (
                    {'title': '用户咨询', 'icon': 'fa fa-question-circle', 'url': self.get_model_url(UserAsk, 'changelist')},
                    {'title': '首页轮播', 'icon': 'fa fa-play', 'url': self.get_model_url(Banner, 'changelist')},
                    {'title': '用户分组', 'icon': 'fa fa-users', 'url': self.get_model_url(Group, 'changelist')},
                    {'title': '用户权限', 'icon': 'fa fa-id-card-o', 'url': self.get_model_url(Permission, 'changelist')},
                    {'title': '日志记录', 'icon': 'fa fa-address-card', 'url': self.get_model_url(Log, 'changelist')},
                )},
        )


# 将model与admin管理器进行关联注册
xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
# 将Xadmin全局管理器与我们的view绑定注册
xadmin.site.register(views.BaseAdminView, BaseSetting)
# 将头部与脚部信息进行注册:
xadmin.site.register(views.CommAdminView, GlobalSettings)
