from .models import User, Event
from django import forms

from django.contrib.auth.forms import UserChangeForm

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ['email', 'password', 'name', 'first_name', 'student_id', 'is_organization']

class ProfileForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = ['email', 'name', 'first_name', 'student_id', 'is_organization', 'avatar']
