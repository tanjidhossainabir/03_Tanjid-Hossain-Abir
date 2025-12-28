from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=50, choices=[('employer', 'Employer'), ('job_seeker', 'Job Seeker')])

    def __str__(self):
        return self.user.username

class EmployerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    company_description = models.TextField()
    company_location = models.CharField(max_length=100)
    company_website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.company_name

class JobSeekerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    skills = models.TextField(help_text="List your skills, separated by commas")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.user_profile.user.username}'s Profile"

class Job(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    number_of_openings = models.PositiveIntegerField()
    category = models.CharField(max_length=100)
    job_description = models.TextField()
    skills_required = models.TextField(help_text="List the required skills, separated by commas")

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    applied_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"{self.applicant} applied for {self.job}"

