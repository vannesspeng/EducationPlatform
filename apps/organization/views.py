from django.core.paginator import PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from django.views.generic.base import View

# 处理课程机构列表的view
from pure_pagination import Paginator

from courses.models import Course
from operation.models import UserAsk, UserFavorite
from organization.forms import UserAskForm
from organization.models import CityDict, CourseOrg, Teacher


class OrgView(View):
    def get(self, request):
        # 查找到所有的课程机构
        all_orgs = CourseOrg.objects.all()
        # 查询热门的机构
        hot_orgs = all_orgs.order_by('-click_nums')[0:3]
        # 查找所有的城市信息
        all_citys = CityDict.objects.all()

        # 搜索关键字
        search_keywords = request.POST.get('keywords', '')
        if search_keywords:
            all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                address__icontains=search_keywords))

        # 如果有city过滤的条件，那么需要加上city过滤
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        # 类别筛选
        category = request.GET.get('ct', "")
        if category:
            # 我们就在机构中作进一步筛选类别
            all_orgs = all_orgs.filter(category=category)

        # 总共有多少家机构使用count进行统计
        org_nums = all_orgs.count()

        #排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_orgs = all_orgs.order_by('-students')
            elif sort == 'courses':
                all_orgs = all_orgs.order_by('-course_nums')

        #对机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        #从all_org中取出5个出来
        p = Paginator(all_orgs, 5, request=request)
        orgs = p.page(page)

        return render(request, "org-list.html", {
            "all_citys": all_citys,
            "all_orgs": orgs,
            'org_nums': org_nums,
            'city_id': city_id,
            'search_keywords': search_keywords,
            'category': category,
            'hot_orgs': hot_orgs
        })


class AddUserAskView(View):
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg": "您的字段有错误，请检查"}', content_type='application/json')


class OrgHomeView(View):
    def get(self, request, org_id):
        # 向前端传值，表明现在在home页
        current_page = "home"
        # 1、根据ID获取机构信息
        course_org = CourseOrg.objects.get(id=org_id)
        # 通过获取的机构信息，直接获取它的所有课程
        all_courses = course_org.course_set.all()[:4]
        all_teachers = course_org.teacher_set.all()[:3]

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-homepage.html', {
            "course_org": course_org,
            "all_courses": all_courses,
            "all_teachers": all_teachers,
            "current_page": current_page,
            "has_fav":has_fav
        })


class OrgCourseView(View):
    def get(self, request, org_id):
        # 向前端传值，表明现在在home页
        current_page = "course"
        course_org = CourseOrg.objects.get(id=org_id)
        all_courses = course_org.course_set.all()

        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-course.html', {
            "current_page": current_page,
            "course_org": course_org,
            "all_courses": all_courses,
            "has_fav": has_fav
        })

class OrgDescView(View):
    def get(self,request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=org_id)
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            "course_org": course_org,
            "current_page": current_page,
            "has_fav": has_fav
        })


class OrgTeacherView(View):
    def get(self,request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=org_id)
        all_teachers = course_org.teacher_set.all()
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-teachers.html', {
            "course_org": course_org,
            "current_page": current_page,
            "all_teachers":all_teachers,
            "has_fav": has_fav
        })


class AddFavView(View):
    def post(self, request):
        id = request.POST.get('fav_id', 0)
        type = request.POST.get('fav_type', 0)

        #收藏与已收藏， 取消收藏
        #判断用户是否登陆，即使没有登录也应该有一个匿名账户
        if not request.user.is_authenticated:
            return HttpResponse(
                '{"status": "fail", "msg": "用户未登录"}', content_type="application/json"
            )
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=id, fav_type=type)
        if exist_records:
            #用户已经收藏了，那说明是要取消收藏
            exist_records.delete()
            # 收藏的减少会导致，课程，教师，机构的喜欢数量变化，所以此处要同步修改
            # 1：表示删除的收藏类型为课程
            if int(type) ==1:
                course = Course.objects.get(id=int(id))
                if course.fav_nums > 0:
                    course.fav_nums -= 1
                else:
                    course.fav_nums = 0
                course.save()

            # 2：表示删除的收藏类型为机构
            if int(type) == 2:
                course_org = CourseOrg.objects.get(id=int(id))
                if course_org.fav_nums > 0:
                    course_org.fav_nums -= 1
                else:
                    course_org.fav_nums = 0
                course_org.save()

            # 3：表示删除的收藏类型为教师
            if int(type) == 3:
                teacher = Teacher.objects.get(id=int(id))
                if teacher.fav_nums > 0:
                    teacher.fav_nums -= 1
                else:
                    teacher.fav_nums = 0
                teacher.save()

            return HttpResponse(
                '{"status": "success", "msg": "收藏"}', content_type="application/json"
            )
        else:
            # 用户未收藏，那么要添加一条收藏记录到数据库中
            user_fav = UserFavorite()
            if int(id) > 0 and int(type) > 0:
                user_fav.fav_id = id
                user_fav.fav_type = type
                user_fav.user = request.user
                user_fav.save()
                # 收藏成功
                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums += 1
                    course.save()
                elif int(type) == 2:
                    org = CourseOrg.objects.get(id=int(id))
                    org.fav_nums += 1
                    org.save()
                elif int(type) == 3:
                    teacher = Teacher.objects.get(id=int(id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse(
                    '{"status": "success", "msg": "已收藏"}', content_type="application/json"
                )
            else:
                return HttpResponse(
                    '{"status": "fail", "msg": "收藏出错"}', content_type="application/json"
                )

