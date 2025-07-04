# core/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, View
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from .models import GoalCategory, Goal, SubCategory
from .forms import RegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import GoalForm
User = get_user_model()


class HomeView(ListView):
    """
    Displays the main home page (index.html).
    It retrieves all GoalCategory objects to display the category grid.
    """
    model = GoalCategory
    template_name = 'index.html'
    context_object_name = 'categories'


class CategoryDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the detail page for a single category.
    
    This view is protected by LoginRequiredMixin, meaning only logged-in users
    can access it. It shows only the goals created by the current user within
    the selected category.
    """
    model = GoalCategory
    template_name = 'category_detail.html'
    context_object_name = 'category' # The object will be available as 'category' in the template

    def get_context_data(self, **kwargs):
        """
        Adds extra context to the template:
        - A list of goals filtered by the current user and category.
        - An instance of the GoalForm for quick goal creation.
        """
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        
        # Get the category object that this view is displaying
        category_object = self.get_object()
        
        # Filter goals to show only those created by the current logged-in user
        # for the current category.
        user_goals = Goal.objects.filter(
            category=category_object, 
            created_by=self.request.user
        )
        
        # Add the filtered goals to the context
        context['goals'] = user_goals
        
        # Add a pre-filled GoalForm to the context for the "quick add" feature.
        # The 'category' field is pre-selected.
        context['goal_form'] = GoalForm(initial={'category': category_object})
        
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


class GoalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Handles the editing of an existing goal.
    
    - LoginRequiredMixin: Ensures the user is logged in.
    - UserPassesTestMixin: Ensures only the user who created the goal can edit it.
    - UpdateView: Provides the core logic for fetching an object and handling form updates.
    """
    model = Goal
    form_class = GoalForm
    template_name = 'goal_form.html' # Reuses the same form template as the create view
    context_object_name = 'goal'

    def test_func(self):
        """
        This is the core security check from UserPassesTestMixin.
        It returns True only if the current user is the creator of the goal.
        If it returns False, Django will show a 403 Forbidden page.
        """
        goal = self.get_object()
        return self.request.user == goal.created_by

    def get_success_url(self):
        """
        Returns the URL to redirect to after the form is successfully updated.
        """
        # Add a success message
        messages.success(self.request, "Maqsad muvaffaqiyatli yangilandi.")
        # Redirect to the detail page of the goal's category
        return reverse_lazy('category_detail', kwargs={'slug': self.object.category.slug})

    def get_context_data(self, **kwargs):
        """
        Adds the page title to the context for the template.
        """
        context = super().get_context_data(**kwargs)
        context['pacge_title'] = "Maqsadni Tahrirlash"
        return context
    
class GoalDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Handles the deletion of an existing goal.
    - LoginRequiredMixin: Ensures the user is logged in.
    - UserPassesTestMixin: Ensures only the goal's creator can delete it.
    - DeleteView: Provides the core logic for displaying a confirmation page 
                  and deleting the object upon POST request.
    """
    model = Goal
    template_name = 'goal_confirm_delete.html' # The template you have in the Canvas
    context_object_name = 'goal'

    def test_func(self):
        """
        Security check from UserPassesTestMixin.
        Returns True only if the current user is the creator of the goal.
        """
        goal = self.get_object()
        return self.request.user == goal.created_by

    def get_success_url(self):
        """
        Returns the URL to redirect to after the goal is successfully deleted.
        We get the category slug *before* the object is deleted to ensure a correct redirect.
        """
        category_slug = self.object.category.slug
        messages.success(self.request, f"'{self.object.title}' maqsadi muvaffaqiyatli o'chirildi.")
        return reverse_lazy('category_detail', kwargs={'slug': category_slug})


from .forms import GoalForm

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = 'goal_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f"'{form.instance.title}' maqsadi muvaffaqiyatli qo'shildi!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('category_detail', kwargs={'slug': self.object.category.slug})

def load_subcategories(request):
    """
    Called via AJAX to load sub-categories based on the selected category.
    """
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)

class SubscribeToGoalView(LoginRequiredMixin, View):
    """
    Handles a user's request to subscribe or unsubscribe from a goal.
    """
    def post(self, request, *args, **kwargs):
        goal_id = self.kwargs.get('goal_id')
        goal = get_object_or_404(Goal, id=goal_id)
        
        if goal.subscribers.filter(id=request.user.id).exists():
            # User is already a subscriber, so unsubscribe them
            goal.subscribers.remove(request.user)
            messages.info(request, f"Siz '{goal.title}' maqsadidan obunani bekor qildingiz.")
        else:
            # User is not a subscriber, so subscribe them
            goal.subscribers.add(request.user)
            messages.success(request, f"Siz '{goal.title}' maqsadiga muvaffaqiyatli obuna bo'ldingiz!")
            
        return redirect(request.META.get('HTTP_REFERER', reverse_lazy('home')))

