from django.db import models
from django.contrib.auth.models import AbstractUser 
# Create your models here.



class Account(AbstractUser): 
    account_type = models.CharField(max_length=100, default="Seeker")  
    saved_jobs = models.ManyToManyField("Job", related_name="saved_jobs", blank=True)
    sex = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True) 
    contact_number = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  
    
    def __str__(self):  
        return f"{self.username} {self.account_type}"
    
    
    
class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=100, blank = True, null = True) 
    salary = models.IntegerField()
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default="Open") 
    slots = models.IntegerField(default=1)
    thumbnail = models.ImageField(upload_to="job_thumbnails", blank=True)    
    
    
    
    def __str__(self):
        return self.title
    
    
class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default="Pending")
    
    def __str__(self):
        return f"{self.job.title} - {self.applicant.username}"  
    
    
    
class Company(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to="company_logos", blank=True)     
    address =  models.CharField(max_length=100)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
    
class UserResume(models.Model): 
    experience = models.TextField() 
    skills = models.TextField() 
    education = models.TextField() 
    user = models.ForeignKey(Account, on_delete=models.CASCADE)