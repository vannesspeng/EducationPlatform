#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:pyy
# datetime:2018/10/11 14:34
from django import forms


class LoginForm(forms.Form):
    # 用户名不能为空
    username = forms.CharField(required=True)
    # password不能小于6位
    password = forms.CharField(required=True, min_length=5)