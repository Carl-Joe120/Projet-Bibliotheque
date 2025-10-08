from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns =[

    path('' , views.loginview , name='loginview'),    
    path('signup/' , views.signupview , name='signup'), 
    path('secretaire/' , views.secretaire , name='secretaire_home'),
    path('redirect_to_membre/' , views.redirect_to_membre , name = 'redirect_to_membre'),
    path('administrateur/' , views.redirect_to_admin , name='admin'),
    path('index/' , views.index , name='index'),
    path('user_profile_setting/' , views.user_profile_setting , name='user_profile_setting'),
    path('user_profile/' , views.user_profile , name='user_profile'),
    path('user_activite/' , views.user_activite , name='user_activite'),
    path('log_out/' , views.log_out , name='log_out')
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
    
