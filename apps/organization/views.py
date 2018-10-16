from django.core.paginator import PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render

from django.views.generic.base import View

# 处理课程机构列表的view
from pure_pagination import Paginator

from organization.models import CityDict, CourseOrg


class OrgView(View):
    def get(self, request):
        # 查找到所有的课程机构
        all_orgs = CourseOrg.objects.all()
        # 总共有多少家机构使用count进行统计
        org_nums = all_orgs.count()
        # 查询热门的机构
        hot_orgs = all_orgs.order_by('click_nums')[:3]
        # 查找所有的城市信息
        all_citys = CityDict.objects.all()

        # 搜索关键字
        search_keywords = request.POST.get('keywords', '')
        if search_keywords:
            all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                address__icontains=search_keywords))


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
        })
