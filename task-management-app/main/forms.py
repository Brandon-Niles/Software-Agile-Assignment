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

    def _parse_time_field(self, value, field_name):
        if not value:
            raise forms.ValidationError({field_name: 'This field cannot be empty.'})
        formats = ['%Y-%m-%d %H:%M', '%Y-%m-%d']
        for f in formats:
            try:
                return datetime.strptime(value, f)
            except Exception:
                continue
        raise forms.ValidationError('Invalid date/time format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM')

    def clean_start_time(self):
        val = self.cleaned_data.get('start_time')
        # will raise ValidationError on bad format
        self._parse_time_field(val, 'start_time')
        return val

    def clean_end_time(self):
        val = self.cleaned_data.get('end_time')
        if not val:
            return val
        self._parse_time_field(val, 'end_time')
        return val

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end:
            # parse again to compare
            s = None
            e = None
            try:
                s = self._parse_time_field(start, 'start_time')
                e = self._parse_time_field(end, 'end_time')
            except forms.ValidationError:
                return cleaned
            if e < s:
                raise forms.ValidationError({'end_time': 'End time must be the same or after start time.'})
        return cleaned


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        if pw and pw2 and pw != pw2:
            self.add_error('password_confirm', 'Passwords do not match')
        return cleaned