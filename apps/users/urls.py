#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:pyy
# datetime:2018/10/23 13:58
from django.urls import path
from users.views import UserInfoView, MyMessageView, MyCourseView, MyFavOrgView, UploadImageView, UpdatePwdView, \
    UpdateEmailView, SendEmailCodeView, MyFavTeacherView, MyFavCourseView

app_name = 'users'

urlpatterns = [
    # 用户信息
    path('info/', UserInfoView.as_view(), name='user_info'),
    # 用户中心我的课程
    path('mycourse/', MyCourseView.as_view(), name="mycourse"),
    # 我收藏的课程
    path('my_message/', MyMessageView.as_view(), name="my_message"),
    # 我收藏的课程机构
    path('myfav/org/', MyFavOrgView.as_view(), name="myfav_org"),
    # 用户头像上传
    path('image/upload/', UploadImageView.as_view(), name="image_upload"),
    path('update/pwd/', UpdatePwdView.as_view(), name="update_pwd"),
    path('sendemail_code/',SendEmailCodeView.as_view(), name="sendemail_code"),
    path('update_email/', UpdateEmailView.as_view(), name="update_email"),
    path('mycourse/', MyCourseView.as_view(), name="mycourse"),
    # 我收藏的课程机构
    path('myfav/org/', MyFavOrgView.as_view(), name="myfav_org"),
    # 我收藏的授课讲师
    path('myfav/teacher/', MyFavTeacherView.as_view(), name="myfav_teacher"),
    # 我收藏的课程
    path('myfav/course/', MyFavCourseView.as_view(), name="myfav_course"),
]
