from django import forms
from .models import UserAccount

class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ['avatar']
