from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 단일 요소는 반드시 쉼표가 있어야 합니다.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = [
        ('프로필', {'fields': ('username', 'password')}),
        ('개인정보', {'fields': ('first_name', 'last_name', 'email')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('로그인정보', {'fields': ('last_login', 'date_joined')}),
    ]