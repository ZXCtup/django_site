from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from users.views import LoginUser, RegisterUserView

app_name='users'

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login' ),
    path('logout/', LogoutView.as_view(), name='logout' ),
    path('register/', RegisterUserView.as_view(), name='register' ),
    
]

# python -m venv venv
# venv/Scripts/acticate


