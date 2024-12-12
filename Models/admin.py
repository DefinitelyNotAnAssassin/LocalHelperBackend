from django.contrib import admin
from .models import Account, Job, JobApplication, Company 


admin.site.register(Account) 
admin.site.register(Job) 
admin.site.register(JobApplication) 
admin.site.register(Company)
