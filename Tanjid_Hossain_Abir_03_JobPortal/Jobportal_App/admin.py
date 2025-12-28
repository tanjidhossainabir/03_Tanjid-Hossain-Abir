from django.contrib import admin
from Jobportal_App.models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(EmployerProfile)
admin.site.register(JobSeekerProfile)
admin.site.register(Job)