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
        path('jobs/<int:id>/remove-saved/', views.remove_saved_job, name='remove_saved_job'),
        path('saved_jobs/', views.saved_jobs, name='saved_jobs'),
        path('jobs_applied/', views.jobs_applied, name='jobs_applied'),
        path('jobs_created/', views.jobs_created, name='jobs_created'), 
        path('jobs_applications/<int:id>/', views.job_application, name='job_application'),
        path('job_applications/<int:id>/accept/', views.accept_application, name='accept_application'), 
        path('job_applications/<int:id>/reject/', views.reject_application, name='reject_application'),
        path('applicant_contact/<int:applicantId>/', views.applicant_contact, name='applicant_contact'),
        path('save_resume', views.save_resume, name='create_resume'),   
        path('get_resume', views.get_resume, name='get_resume'),
        path('applicant_resume/<int:id>/', views.applicant_resume, name='applicant_resume/'),
        path('change_status/<int:id>/', views.change_status, name='change_status'),
        path('close_job', views.close_job, name='close_job'),
        path('saveProfile', views.save_profile, name='save_profile'),
        path('adminDashboard', views.admin_dashboard, name='admin_dashboard'),
        path('jobs/<int:id>/update/', views.update_job, name='update_job'),
        path('verify-email', views.verify_email, name='verify_email'),
        path('job_applications/<int:id>/cancel/', views.cancel_application, name='cancel_application'),
        path('jobs/<int:id>/check-status/', views.check_job_status, name='check_job_status'),
        path('remove_resume_attachment', views.remove_resume_attachment, name='remove_resume_attachment'),
        path('updateProfilePicture', views.update_profile_picture, name='update_profile_picture'),
    ]