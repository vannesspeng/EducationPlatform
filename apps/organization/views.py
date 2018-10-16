from django.core.paginator import PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from django.views.generic.base import View

# 处理课程机构列表的view
from pure_pagination import Paginator

from operation.models import UserAsk
from organization.forms import UserAskForm
from organization.models import CityDict, CourseOrg


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
