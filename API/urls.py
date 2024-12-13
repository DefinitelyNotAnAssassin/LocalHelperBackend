from django.urls import path 
from . import views 


urlpatterns = [ 
               
        path('jobs/', views.jobs, name='job_list'),    
        path('login', views.login, name='login'),     
        path('signup', views.signup, name='signup'),    
        path('token/refresh/', views.refresh_token, name='refresh_token'),
        path('verifyAuth', views.verify_auth, name='verify_auth'),
        path('jobs/<int:id>/', views.job, name='job'),
        path('jobs/<int:id>/apply/', views.apply_job, name='apply_job'),
        path('jobs/<int:id>/save/', views.save_job, name='save_job'),
        path('saved_jobs/', views.saved_jobs, name='saved_jobs'),
        path('jobs_applied/', views.jobs_applied, name='jobs_applied'),
        path('hello_world', views.hello_world, name='hello_world'),
    ]