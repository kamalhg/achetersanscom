from django import forms
from .models import UserProfile
from django.utils.translation import ugettext_lazy as _

class EditUserAccountForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', )
