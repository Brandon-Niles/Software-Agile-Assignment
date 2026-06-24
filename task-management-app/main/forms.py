from django import forms
from django.contrib.auth.models import User
from .models import Task
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'platform', 'location', 'status', 'start_time', 'end_time', 'retries']

    def clean_retries(self):
        retries = self.cleaned_data.get('retries')
        if retries is None:
            return 0
        if retries < 0:
            raise forms.ValidationError('Retries must be zero or positive')
        return retries


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password