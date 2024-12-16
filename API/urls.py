from django.urls import path 
from . import views 


urlpatterns = [ 
               
        path('jobs/', views.jobs, name='job_list'),    
        path('login', views.login, name='login'),     
        path('signup', views.signup, name='signup'),    
        path('token/refresh/', views.refresh_token, name='refresh_token'),
        path('verifyAuth', views.verify_auth, name='verify_auth'),
        path("create_job", views.create_job, name="create_job"),    
        path('jobs/<int:id>/', views.job, name='job'),
        path('jobs/<int:id>/apply/', views.apply_job, name='apply_job'),
        path('jobs/<int:id>/save/', views.save_job, name='save_job'),
        path('saved_jobs/', views.saved_jobs, name='saved_jobs'),
        path('jobs_applied/', views.jobs_applied, name='jobs_applied'),
        path('jobs_created/', views.jobs_created, name='jobs_created'), 
        path('jobs_applications/<int:id>/', views.job_application, name='job_application'),
        path('job_applications/<int:id>/accept/', views.accept_application, name='accept_application'), 
        path('job_applications/<int:id>/reject/', views.reject_application, name='reject_application'),
        path('save_resume', views.save_resume, name='create_resume'),   
        path('get_resume', views.get_resume, name='get_resume'),
        path('applicant_resume/<int:id>/', views.applicant_resume, name='applicant_resume/'),
        path('change_status/<int:id>/', views.change_status, name='change_status'),
        path('close_job', views.close_job, name='close_job'),
    ]