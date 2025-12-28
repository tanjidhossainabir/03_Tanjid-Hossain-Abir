from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import *

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_description', 'company_location', 'company_website']

class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['skills', 'resume', 'photo']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'number_of_openings', 'category', 'job_description', 'skills_required']

class JobSearchForm(forms.Form):
    keyword = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search by title or skills'}))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Filter by category'}))


class RegistrationForm(UserCreationForm):
    display_name = forms.CharField(max_length=100, required=True)
    user_type = forms.ChoiceField(choices=[('employer', 'Employer'), ('job_seeker', 'Job Seeker')], required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'display_name', 'user_type', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                display_name=self.cleaned_data.get('display_name'),
                user_type=self.cleaned_data.get('user_type')
            )
        return user
