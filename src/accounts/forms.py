from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=200,label='Email Confirmation', help_text='Required')
    username = forms.CharField(
        label="Email",
        strip=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Email'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Email'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Re Enter Password'})

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        elif username != email:
            raise ValidationError("Email Does Not Match")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password1', 'password2')
