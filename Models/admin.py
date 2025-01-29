from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Job, JobApplication, Company, UserResume

admin.site.register(Account) 
admin.site.register(Job) 
admin.site.register(JobApplication) 
admin.site.register(Company)
admin.site.register(UserResume)
