#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:pyy
# datetime:2018/10/17 15:48
from django.urls import path
from courses.views import CourseListView

app_name = "courses"

urlpatterns = [
    path('list/', CourseListView.as_view(), name='list'),
]