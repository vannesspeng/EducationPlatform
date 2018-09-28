from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    GENDER_CHOICES = (
        ("male", u"男"),
        ("female", u"女"),
    )

    nike_name = models.CharField(max_length=50, verbose_name="昵称", default="")
    birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    gender = models.CharField(
        max_length=5,
        verbose_name=u"性别",
        choices=GENDER_CHOICES,
        default="female"
    )
    address = models.CharField(max_length=100, null=True, blank=True, default="")
    mobile = models.CharField(max_length=11, null=True, blank=True)
    image = models.ImageField(
        upload_to="image/%Y/%m/",
        default="image/default.png",
        max_length=100
    )

    class Meta:
        verbose_name = "用户信息",
        verbose_name_plural = verbose_name

    # 重载Unicode方法，打印实例会打印实例的username属性，username继承自
    def __str__(self):
        print(self.username)


class EmailVerifyRecord(models.Model):
    SEND_CHOICES = (
        ("register", u"注册"),
        ("forget", u"找回密码")
    )
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    # 未设置null = true blank = true 默认不可为空
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    send_type = models.CharField(choices=SEND_CHOICES, max_length=10)
    # 这里的now得去掉(),不去掉会根据编译时间。而不是根据实例化时间。
    send_time = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = "邮箱验证码"
        verbose_name_plural = verbose_name


# 轮播图model


class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name=u"标题")
    image = models.ImageField(
        upload_to="banner/%Y/%m",
        verbose_name=u"轮播图",
        max_length=100)
    url = models.URLField(max_length=200, verbose_name=u"访问地址")
    # 默认index很大靠后。想要靠前修改index值。
    index = models.IntegerField(default=100, verbose_name=u"顺序")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"轮播图"
        verbose_name_plural = verbose_name
