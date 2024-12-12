from django.urls import path 
from . import views 


urlpatterns = [ 
               
        path('jobs/', views.jobs, name='job_list'),    
        path('login', views.login, name='login'),     
        path('signup', views.signup, name='signup'),    
        path('token/refresh/', views.refresh_token, name='refresh_token'),
        path('verifyAuth', views.verify_auth, name='verify_auth'),
    ]