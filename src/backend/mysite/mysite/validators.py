from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    def __init__(self, min_length=8, max_length=25):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password, user=None):
        if not self.min_length <= len(password) <= self.max_length:
            raise ValidationError(
                (f"パスワードは{self.min_length}文字以上{self.max_length}文字以内である必要があります。"),
            )
        if not re.match(r'^[a-zA-Z0-9]+$', password):
            raise ValidationError("パスワードは半角英数字のみを含む必要があります。")

    def get_help_text(self):
        return _(f"パスワードは{self.min_length}文字以上{self.max_length}文字以内で、半角英数字のみを使用してください。")