from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
#from django_otp.plugins.otp_totp.models import TOTPDevice
#from django_otp.admin import OTPAdminSite
#from django_otp.admin import OTPAdminMixin

User = get_user_model()

class UserAdminCustom(UserAdmin):
    # ユーザー詳細
    fieldsets = (
        (None, {
            "fields": (
                "name",
                "email",
                "password",
                "is_active",
                "is_staff",
                "is_superuser"
            )
        }),
    )

    # ユーザー追加
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "name",
                "email",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    # ユーザー一覧
    list_display = (
        "id",
        "name",
        "email",
        "is_active",
    )

    list_filter = ()
    # 検索
    search_fields = ("email", )
    # 順番
    ordering = ("id", )

admin.site.register(User, UserAdminCustom)

# OTPAdminSiteを使用するための設定
#admin.site.__class__ = OTPAdminSite