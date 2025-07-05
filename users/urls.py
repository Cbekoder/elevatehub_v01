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
    # New URL for the Goal Detail page
    path("goal/<int:pk>/", views.GoalDetailView.as_view(), name="goal_detail"),
    path("goal/new/", views.GoalCreateView.as_view(), name="goal_create"),
    path("goal/<int:pk>/edit/", views.GoalUpdateView.as_view(), name="goal_update"),
    path("goal/<int:pk>/delete/", views.GoalDeleteView.as_view(), name="goal_delete"),
    path(
        "goal/<int:goal_id>/checkin/", views.CheckInView.as_view(), name="goal_checkin"
    ),
    # Logout View
    path(
        "logout/",
        LogoutView.as_view(next_page='login'),
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
    path(
        "goal/<int:goal_id>/post_message/",
        views.PostMessageView.as_view(),
        name="post_message",
    ),
    path(
        "goal/<int:goal_id>/fetch_messages/",
        views.FetchMessagesView.as_view(),
        name="fetch_messages",
    ),

     path('goal/<int:goal_pk>/subtask/new/', views.SubTaskCreateView.as_view(), name='subtask_create'),
    path('subtask/<int:subtask_pk>/toggle/', views.SubTaskToggleView.as_view(), name='subtask_toggle'),
]
