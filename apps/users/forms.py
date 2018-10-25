#!/usr/bin/env python
#-*- coding:utf-8 -*-
# author:pyy
# datetime:2018/10/11 14:34
from captcha.fields import CaptchaField
from django import forms

from users.models import UserProfile


class LoginForm(forms.Form):
    # 用户名不能为空
    username = forms.CharField(required=True)
    # password不能小于6位
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误", 'required': u'验证码不能为空'})

# 激活时验证码实现
class ActiveForm(forms.Form):
    # 激活时不对邮箱密码做验证
    # 应用验证码 自定义错误输出key必须与异常一样
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


class ForgetForm(forms.Form):
    email = forms.CharField(error_messages={'required': u'邮箱不能为空'})
    captcha = CaptchaField(error_messages={'invalid': u'验证码错误', 'required': u'验证码不能为空'})

class ModifyPwdForm(forms.Form):
    new_psw = forms.CharField(required=True, min_length=5, error_messages={'required': u'新密码不能为空'})
    new_psw_confirm = forms.CharField(required=True, min_length=5, error_messages={'required': u'新密码确认不能为空'})

# 用于文件上传，修改头像
class UploadImageForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['image']


# 用于个人中心修改个人信息
class UserInfoForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['nick_name','gender','birthday','address','mobile']
