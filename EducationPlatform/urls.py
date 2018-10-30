"""EducationPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include, re_path
from django.views.static import serve
import xadmin
from EducationPlatform.settings import MEDIA_ROOT
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, PswResetView, ModifyPwdView, LogoutView, \
    IndexView

urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name='register'),
    # 验证码url
    path('captcha/', include('captcha.urls')),
    re_path(r'^active/(?P<active_code>[a-zA-Z0-9]*)/$', ActiveUserView.as_view(), name='user_active'),
    path('forget/', ForgetPwdView.as_view(), name='forget_pwd'),
    re_path('reset/(?P<active_code>.*)/', PswResetView.as_view(), name="reset_pwd"),
    path('modify_pwd/', ModifyPwdView.as_view(), name="modify_pwd"),
    re_path(r'^media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
    # 课程机构app的url配置，讲师的也在里面
    path('org/', include('organization.urls', namespace='org')),
    path('course/', include('courses.urls', namespace='course')),
    path('user/', include('users.urls', namespace='user')),
    # 配置静态文件上传的访问处理url
    re_path('static/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
    # 配置文件上传的访问处理url
    # re_path('media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
    # 富文本相关path配置
    path("ueditor/", include('DjangoUeditor.urls')),
]
