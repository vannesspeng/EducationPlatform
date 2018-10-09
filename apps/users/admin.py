from django.contrib import admin
from .models import UserProfile
# Register your models here.

# 定义一个管理器命名
class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserProfile, UserProfileAdmin)