from django.forms import ModelForm, TextInput, EmailInput
from django.contrib.auth.models import User
from .models import Profile


class UserProfileForm(ModelForm):
    class Meta:
        model = Profile

        fields = ['avatar', ]


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control', 'readonly': 'True'}),
        }
