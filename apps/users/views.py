import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
#当我们配置这个url被这个view处理时，自动传入request对象
from django.urls import reverse
from django.views.generic.base import View
import threading

from pure_pagination import Paginator

from courses.models import Course
from operation.models import UserMessage, UserCourse, UserFavorite
from organization.models import CourseOrg, Teacher
from users.forms import LoginForm, RegisterForm, ActiveForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from users.models import UserProfile, EmailVerifyRecord, Banner
from utils.email_send import send_register_eamil


class LoginView(View):
    def get(self, request):
        redirect_url = request.GET.get('next', '')
        return render(request, 'login.html', {
            'redirect_url': redirect_url
        })


    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # 从request的POST对象中获取用户名和密码
            user_name = request.POST.get('username', '')
            password = request.POST.get('password', '')
            # 调用Django自带的验证方法
            user = authenticate(request, username=user_name, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    redirect_url = request.POST.get('next', '')
                    if redirect_url:
                        return HttpResponseRedirect(redirect_url)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, 'login.html', {'msg': '用户未激活'})
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
            users = UserProfile.objects.filter(username=user_name)
            if not users:
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
                user_message.message = "欢迎注册Isudynet小站!! --系统自动消息"
                user_message.save()

                # 新建一个线程发送注册激活邮件
                send_email_thread = SendEmailThread(email=user_name, type='register')
                send_email_thread.start()
                # 跳转到登录页面
                return render(request, "login.html")
            else:
                return render(request, 'register.html', {'msg': '用户名已经注册', 'register_form': register_form})
        else:
            return render(request, 'register.html', {'register_form': register_form})

class SendEmailThread(threading.Thread):
    def __init__(self, email, type):
        threading.Thread.__init__(self)
        self.email = email
        self.type = type


    def run(self):
        send_register_eamil(self.email, "register")

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
                return render(request, "login.html", {"msg": "激活成功，请重新登陆"})
        # 自己瞎输的激活码
        else:
            return render(
                request, "register.html", {
                    "msg": "您的激活链接无效", 'active_form': active_form})


class ForgetPwdView(View):
    def get(self, request):
        active_form = ActiveForm(request.POST)
        return render(request, 'forgetpwd.html', {'active_form': active_form})


    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            results = UserProfile.objects.filter(email=email)
            if not results:
                return render(request, 'forgetpwd.html', {'msg': '邮箱未注册!', 'forget_form': forget_form})
            else:
                # 发送邮件
                send_email_thread = SendEmailThread(email=email, type='forget')
                send_email_thread.start()
                #send_register_eamil(email, 'forget')
                return render(request, "login.html", {"msg": "重置密码邮件已发送,请注意查收!"})
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})

class PswResetView(View):
    def get(self, request, active_code):
        all_record = EmailVerifyRecord.objects.filter(code=active_code)
        # 如果不为空也就是有用户
        active_form = ActiveForm(request.GET)
        if all_record:
            # 获取对应的邮箱
            for record in all_record:
                email = record.email
                return render(request, 'password_reset.html', {'active_code': active_code})
        else:
            return render(
                request, "forgetpwd.html", {
                    "msg": "您的重置密码链接无效,请重新请求", "active_form": active_form})



class ModifyPwdView(View):
    def post(self, request):
        modify_psw_form = ModifyPwdForm(request.POST)
        if modify_psw_form.is_valid():
            new_psw = request.POST.get("new_psw", "")
            new_psw_confirm = request.POST.get("new_psw_confirm", "")
            active_code = request.POST.get("active_code", "")
            # 如果两次密码不相等，返回错误信息
            if new_psw != new_psw_confirm:
                return render(
                    request, "password_reset.html", {
                        'active_code':active_code, "msg": "两次输入的密码不一致"})
            # 新密码两次输入不一致，返回错误信息
            # 如果密码一致
            # 找到激活码对应的邮箱
            all_record = EmailVerifyRecord.objects.filter(code=active_code)
            for record in all_record:
                email = record.email
            user = UserProfile.objects.get(email=email)
            # 加密成密文
            user.password = make_password(new_psw)
            # save保存到数据库
            user.save()
            return render(request, "login.html", {"msg": "密码修改成功，请登录!"})
        # 验证失败说明密码位数不够。
        else:
            return render(request, 'password_reset.html', {'modify_psw_form': modify_psw_form})

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

class UserInfoView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'next'
    def get(self, request):
        return render(request, 'usercenter-info.html', {})


    def post(self, request):
        # 不像用户咨询是一个新的。需要指明instance。不然无法修改，而是新增用户
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse(
                '{"status":"success"}',
                content_type='application/json')
        else:
            # 通过json的dumps方法把字典转换为json字符串
            return HttpResponse(
                json.dumps(
                    user_info_form.errors),
                content_type='application/json')

class UploadImageView(View, LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'next'
    def post(self,request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type="application/json")
        else:
            return HttpResponse('{"status":"fail"}', content_type="application/json")

class UpdatePwdView(View, LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        modify_pwd_form = ModifyPwdForm(request.POST)
        if modify_pwd_form.is_valid():
            psw1 = request.POST.get('new_psw', '')
            psw2 = request.POST.get('new_psw_confirm', '')
            if psw1 != psw2:
                return HttpResponse('{"status":"fail", "msg":"两次输入的密码不一致"}', content_type="application/json")
            user = request.user
            user.password = make_password(psw2)
            user.save()
            return HttpResponse('{"status":"success"}', content_type="application/json")
        else:
            return HttpResponse(json.dumps(modify_pwd_form.errors), content_type="application/json")


class SendEmailCodeView(LoginRequiredMixin, View):
    def get(self, request):
        # 取出需要发送的邮件
        email = request.GET.get("email", "")

        # 不能是已注册的邮箱
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')
        send_register_eamil(email, "update_email")
        return HttpResponse('{"status":"success"}', content_type='application/json')

class UpdateEmailView(View, LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码无效"}', content_type='application/json')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))

class MyCourseView(View, LoginRequiredMixin):
    login_url = "/login/"
    redirect_field_name = "next"
    def get(self, reqeust):
        user_courses = UserCourse.objects.filter(user=reqeust.user)
        return render(reqeust, 'usercenter-mycourse.html', {'user_courses': user_courses})


class MyFavOrgView(View, LoginRequiredMixin):
    login_url = "/login/"
    redirect_field_name = "next"
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org = CourseOrg.objects.get(id=fav_org.fav_id)
            if org:
                org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {'org_list': org_list})


class MyFavTeacherView(View, LoginRequiredMixin):
    login_url = "/login/"
    redirect_field_name = "next"

    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher = Teacher.objects.get(id=fav_teacher.fav_id)
            if teacher:
                teacher_list.append(teacher)
        return render(request, 'usercenter-fav-teacher.html', {'teacher_list': teacher_list})

class MyFavCourseView(View, LoginRequiredMixin):
    login_url = "/login/"
    redirect_field_name = "next"

    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course = Course.objects.get(id=fav_course.fav_id)
            if course:
                course_list.append(course)
        return render(request, 'usercenter-fav-course.html', {'course_list': course_list})


class MyMessageView(View, LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = "next"

    def get(self, request):
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()
        messages = UserMessage.objects.filter(user=request.user.id)
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(messages, 8, request=request)
        messages = p.page(page)
        return render(request, 'usercenter-message.html', {'messages': messages})

class IndexView(View):
    def get(self, request):
        all_banner = Banner.objects.all().order_by('index')[:5]
        # 正常位课程
        courses = Course.objects.filter(is_banner=False)[:6]
        # 轮播图课程取三个
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        # 课程机构
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            "all_banner": all_banner,
            "courses": courses,
            "banner_courses": banner_courses,
            "course_orgs": course_orgs,
        })