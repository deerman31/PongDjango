from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator, EmailValidator
import pyotp
import os
from django.conf import settings
from django.core.exceptions import ValidationError
import re

class UserManager(BaseUserManager):
    #アカウント登録されるとこの関数がコールされる
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("メールアドレスは必須です")
        if not name:
            raise ValueError("名前は必須です")

        email = self.normalize_email(email)
        email = email.lower()
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    # 管理者アカウント作成時に呼ばれる
    def create_superuser(self, email, name, password=None, **extra_fields):
        user = self.model(email=email, name=name, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

def validate_username(value):
    if not value.isalnum() or len(value) < 4 or len(value) > 15:
        raise ValidationError('名前は半角英数字のみで4文字以上15文字以内である必要があります。')


from django.utils import timezone

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("メールアドレス", max_length=255, unique=True, validators=[EmailValidator])
    name = models.CharField("名前", max_length=15, unique=True, validators=[validate_username])

    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def save(self, *args, **kwargs):
        # 新しいアバターがアップロードされた場合、古いファイルを削除する
        if self.pk:
            old_avatar = UserAccount.objects.filter(pk=self.pk).values_list('avatar', flat=True).first()
            if old_avatar and old_avatar != self.avatar.name:
                old_avatar_path = os.path.join(settings.MEDIA_ROOT, old_avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)

        super().save(*args, **kwargs)

    otp_secret = models.CharField(max_length=32, blank=True, null=True)  # 長さを32に増やす
    is_2fa_enabled = models.BooleanField(default=False)

    is_oauth = models.BooleanField(default=False)

    def generate_otp_secret(self):
        self.otp_secret = pyotp.random_base32()
        self.save()
        return self.otp_secret

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    friends = models.ManyToManyField('self', symmetrical=False, related_name='friend_set', blank=True)
    friend_requests_sent = models.ManyToManyField('self', symmetrical=False, related_name='friend_requests_received', blank=True)

    objects = UserManager()

    # ログインしているかどうかをチェックする ログインしていたら、True
    is_online = models.BooleanField(default=False)

    last_activity = models.DateTimeField(default=timezone.now)

    # メールアドレスと名前を必須項目に
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def set_online(self):
        self.is_online = True
        self.last_activity = timezone.now()
        self.save()

    def set_offline(self):
        self.is_online = False
        self.last_activity = timezone.now()
        self.save()

    def __str__(self):
        return self.email

from django.utils import timezone
class GameResult(models.Model):
    winner = models.CharField(max_length=150)
    loser = models.CharField(max_length=150)
    date_time = models.DateTimeField(auto_now_add=True)
    winner_score = models.IntegerField(default=0)
    loser_score = models.IntegerField(default=0)

    def record_result(self, win_username, lose_username, win_score, lose_score):
        self.winner = win_username
        self.loser = lose_username
        self.date_time = timezone.now()
        self.winner_score = win_score
        self.loser_score = lose_score
        self.save()
    
    def __str__(self):
        return f"Winner: {self.winner} ({self.winner_score}), Loser: {self.loser} ({self.loser_score}), Date: {self.date_time}"
    
    @classmethod
    def get_all_results(cls):
        results = cls.objects.all()
        for result in results:
            print(result)

    @classmethod
    def get_results_by_username(cls, username):
        return cls.objects.filter(models.Q(winner=username) | models.Q(loser=username))

class RockPaperScissorsResult(models.Model):
    winner = models.CharField(max_length=150)
    loser = models.CharField(max_length=150)
    date_time = models.DateTimeField(auto_now_add=True)
    winner_score = models.IntegerField(default=0)
    loser_score = models.IntegerField(default=0)

    def record_result(self, win_username, lose_username, win_score, lose_score):
        self.winner = win_username
        self.loser = lose_username
        self.date_time = timezone.now()
        self.winner_score = win_score
        self.loser_score = lose_score
        self.save()
    
    def __str__(self):
        return f"Winner: {self.winner} ({self.winner_score}), Loser: {self.loser} ({self.loser_score}), Date: {self.date_time}"
    
    @classmethod
    def get_all_results(cls):
        results = cls.objects.all()
        for result in results:
            print(result)

    @classmethod
    def get_results_by_username(cls, username):
        return cls.objects.filter(models.Q(winner=username) | models.Q(loser=username))
