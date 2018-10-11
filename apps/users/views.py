from django.contrib.auth import authenticate, login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.shortcuts import render
#当我们配置这个url被这个view处理时，自动传入request对象
from django.views.generic.base import View

from operation.models import UserMessage
from users.forms import LoginForm, RegisterForm, ActiveForm
from users.models import UserProfile, EmailVerifyRecord
from utils.email_send import send_register_eamil


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


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            password = request.POST.get('password', '')

            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.password = make_password(password)

            # 默认激活状态为false
            user_profile.is_active = False

            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册mtianyan慕课小站!! --系统自动消息"
            user_message.save()

            # 发送注册激活邮件
            send_register_eamil(user_name, "register")
            # 跳转到登录页面
            return render(request, "login.html")
        else:
            return render(request, 'register.html', {'register_form': register_form})

# 激活用户的view
class ActiveUserView(View):
    def get(self, request, active_code):
        # 查询邮箱验证记录是否存在
        all_record = EmailVerifyRecord.objects.filter(code = active_code)
        # 激活form负责给激活跳转进来的人加验证码
        active_form = ActiveForm(request.GET)
        # 如果不为空也就是有用户
        if all_record:
            for record in all_record:
                # 获取到对应的邮箱
                email = record.email
                # 查找到邮箱对应的user
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
                # 激活成功跳转到登录页面
                return render(request, "login.html", )
        # 自己瞎输的验证码
        else:
            return render(request, "register.html", {"msg": "您的激活链接无效","active_form": active_form})


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

