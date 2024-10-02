from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from .views.two_fa import otp_setup, generate_qr_code, verify_otp, disable_2fa
from .views.oauth_views import OauthLoginView, CallbackView
from .views.friend_view import search_users, send_friend_request, respond_friend_request, friend_list, friend_requests_list
from .views.logout_view import LogoutView
from .views.signup_view import SignupView
from .views.login_view import LoginView
from .views.verify_token_view import VerifyTokenView
from .views.refresh_token_view import RefreshTokenView
from .views.delete_user_view import DeleteUserView
from .views.get_user_name_view import GetUserNameView
from .views.get_user_email_view import GetUserEmailView
from .views.set_avatar_view import SetAvatarView
from .views.update_email_view import UpdateEmailView
from .views.update_name_view import UpdateNameView
from .views.get_avatar_view import GetAvatarView
from .views.delete_avatar_view import DeleteAvatarView
from .views.update_password_view import UpdatePasswordView
from .views.history_view import get_user_game_results
from .views.rps_history_view import get_user_rps_results

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("jwt/refresh/", RefreshTokenView.as_view()),
    path("jwt/verify/", VerifyTokenView.as_view()),
    path("get/name/", GetUserNameView.as_view()),
    path("get/email/", GetUserEmailView.as_view()),
    path("get/avatar/", GetAvatarView.as_view()),

    path("update/name/", UpdateNameView.as_view()),
    path("update/email/", UpdateEmailView.as_view()),
    path("update/password/", UpdatePasswordView.as_view()),
    path("set/avatar/", SetAvatarView.as_view()),

    path("delete/avatar/", DeleteAvatarView.as_view()),
    path("delete/user/", DeleteUserView.as_view()),

    path('logout/', LogoutView.as_view(), name='logout'),

    path("user_infomation/", TemplateView.as_view(template_name='accounts/user_infomation.html'), name="user_infomation"),

    path('otp-setup/', otp_setup, name='otp_setup'),

    path('generate-qr-code/', generate_qr_code, name='generate_qr_code'),

    path('verify-otp/', verify_otp, name='verify_otp'),

    path('disable-2fa/', disable_2fa, name='disable_2fa'),

    # 42 API OAuth 2.0
    path('oauth/login/', OauthLoginView.as_view(), name='oauth_login'),  # クラスベースのビューを使用
    path('callback/', CallbackView.as_view(), name='oauth_callback'),  # クラスベースのビューを使用

    # friend
    path('friends/', friend_list, name='friend_list'),
    path('friend_requests/', friend_requests_list, name='friend_requests_list'),
    path('search/', search_users, name='search_users'),
    path('send_request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('respond_request/<int:user_id>/<str:action>/', respond_friend_request, name='respond_friend_request'),
    path('game_result/', get_user_game_results, name='game_result'),
    path('rps_game_result/', get_user_rps_results, name='rps_result'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)