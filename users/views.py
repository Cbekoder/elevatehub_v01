# core/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from .models import GoalCategory, Goal
from .forms import RegistrationForm

User = get_user_model()


class HomeView(ListView):
    """
    Displays the main home page (index.html).
    It retrieves all GoalCategory objects to display the category grid.
    """
    model = GoalCategory
    template_name = 'index.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    """
    Displays the detail page for a single category, showing all goals
    associated with it.
    """
    model = GoalCategory
    template_name = 'category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the goals for this category
        context['goals'] = Goal.objects.filter(category=self.get_object())
        return context


class RegisterView(View):
    """
    Handles user registration.
    GET: Displays the registration form.
    POST: Processes the form, creates a new user, and logs them in.
    """
    form_class = RegistrationForm
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        # If user is already authenticated, redirect them to the home page
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            password = form.cleaned_data.get('password')

            try:
                # Create the user. Username is set to the email for uniqueness.
                user = User.objects.create_user(
                    username=email, 
                    email=email, 
                    password=password, 
                    first_name=first_name
                )
                
                # Log the newly created user in automatically
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {first_name}! Hisobingiz muvaffaqiyatli yaratildi.")
                
                # Redirect to the home page after successful registration
                return redirect('home')

            except Exception as e:
                # Handle potential, though unlikely, errors during user creation
                messages.error(request, "Hisob yaratishda kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")
                
        # If form is invalid, re-render the page with the form and its errors
        return render(request, self.template_name, {'form': form})
