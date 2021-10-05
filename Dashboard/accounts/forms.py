from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, \
    SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()


# Login
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  


# Signup
class SignupForm(UserCreationForm):
    last_name = forms.CharField(label="Last Name")
    first_name = forms.CharField(label="First Name")
    username = forms.CharField(label="Username")

    class Meta:
        model = User
        fields = ('email', 'last_name', 'first_name', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email


# PasswordReset
class PasswordResetForm(PasswordResetForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PasswordResetConfirmForm(SetPasswordForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProfileForm(forms.ModelForm):
    last_name = forms.CharField(label="Last Name")
    first_name = forms.CharField(label="First Name")
    username = forms.CharField(label="Username")
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'username', 'email')
        unique = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
