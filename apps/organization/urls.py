#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:pyy
# datetime:2018/10/16 11:18
from django.urls import path

from organization.views import OrgView, AddUserAskView

app_name = "organization"


urlpatterns = [
    # 课程机构列表url
    path('list/', OrgView.as_view(), name="org_list"),
    path('add_ask/', AddUserAskView.as_view(), name="add_ask"),
]