from django import forms
from django.contrib.auth.models import User
from .models import Task
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime


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

    def _parse_time_value(self, value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        for fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%d'):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise forms.ValidationError('Invalid date/time format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM')

    def clean_start_time(self):
        value = self.cleaned_data.get('start_time')
        self._parse_time_value(value)
        return value

    def clean_end_time(self):
        value = self.cleaned_data.get('end_time')
        if value:
            self._parse_time_value(value)
        return value

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time:
            parsed_start = self._parse_time_value(start_time)
            parsed_end = self._parse_time_value(end_time)
            if parsed_end < parsed_start:
                self.add_error('end_time', 'End time must be the same or after start time.')
        return cleaned_data


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