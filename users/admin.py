from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    ordering = ("id",)
    list_display = ("id", "username", "phone", "email", "telegram_id", "is_active", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (_("Personal info"), {"fields": ("email", "telegram_id")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "email", "telegram_id", "password1", "password2", "is_active", "is_staff"),
        }),
    )

    search_fields = ("username", "phone", "email", "telegram_id")
