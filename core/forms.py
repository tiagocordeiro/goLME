from django.contrib.auth.models import User
from django.forms import EmailInput, ModelForm, TextInput, CheckboxInput

from .models import Profile


class UserProfileForm(ModelForm):
    class Meta:
        model = Profile

        fields = ['avatar', 'api_view', 'api_secret_key', 'site_url']

        widgets = {
            'api_view': CheckboxInput(attrs={'readoly': 'True', 'readonly': 'True'}),
            'api_secret_key': TextInput(attrs={'class': 'form-control', 'readonly': 'True'}),
            'site_url': TextInput(attrs={'class': 'form-control', 'readonly': 'True'})
        }


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': EmailInput(attrs={'class': 'form-control', 'readonly': 'True'}),
        }
