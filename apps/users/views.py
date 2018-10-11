from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.shortcuts import render
#当我们配置这个url被这个view处理时，自动传入request对象
from django.views.generic.base import View

from users.forms import LoginForm
from users.models import UserProfile

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html', {})


    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 从request的POST对象中获取用户名和密码
            user_name = request.POST.get('username', '')
            password = request.POST.get('password', '')
            # 调用Django自带的验证方法
            user = authenticate(request, username=user_name, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'index.html')
            else:
                return render(request, 'login.html', {'msg': '用户名或者密码错误！'})
        else:
            return render(request, 'login.html', {'login_form': login_form})



class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因，Q为使用并集查询
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            # django后台中密码加密，所以不能用password=password
            # UserProfile集成AbstractUser中有定义一个check_password(self, raw_password)
            if user.check_password(password):
                return user
        except Exception as e:
            return None

