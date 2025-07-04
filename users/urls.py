# core/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from users.forms import LoginForm
from . import views

urlpatterns = [
    # Home and Category URLs
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "login/",
        LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm,  # Use our custom form
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path("goal/new/", views.GoalCreateView.as_view(), name="goal_create"),
    path("goal/<int:pk>/edit/", views.GoalUpdateView.as_view(), name="goal_update"),
    path("goal/<int:pk>/delete/", views.GoalDeleteView.as_view(), name="goal_delete"),
    # Logout View
    path(
        "logout/",
        LogoutView.as_view(
            template_name="registration/logout.html"  # Path to the logout confirmation page
        ),
        name="logout",
    ),
    path(
        "goal/<int:goal_id>/subscribe/",
        views.SubscribeToGoalView.as_view(),
        name="goal_subscribe",
    ),
    # AJAX URL
    path(
        "ajax/load-subcategories/",
        views.load_subcategories,
        name="ajax_load_subcategories",
    ),
]
