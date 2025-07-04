# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from users.forms import LoginForm
from . import views

urlpatterns = [
    # Home and Category URLs
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    path(
        'login/', 
        LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=LoginForm, # Use our custom form
            redirect_authenticated_user=True
        ), 
        name='login'
    ),

    # Logout View
    path(
        'logout/', 
        LogoutView.as_view(
            template_name='registration/logout.html' # Path to the logout confirmation page
        ), 
        name='logout'
    ),
]
