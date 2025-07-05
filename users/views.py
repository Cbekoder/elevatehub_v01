# core/views.py
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, View
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.contrib import messages

from users.services import add_xp_and_check_level_up, grant_achievement
from .models import GoalCategory, Goal, GoalMessage, SubCategory, SubTask
from .forms import MessageForm, RegistrationForm, SubTaskForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import GoalForm
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .models import Goal, GoalStreak
from .models import Achievement, UserAchievement

User = get_user_model()


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Displays a rich, data-driven profile page for the authenticated user.
    """
    model = User
    template_name = 'profile_detail.html'
    context_object_name = 'profile_user'

    def get_object(self):
        # The view will always display the profile of the currently logged-in user.
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        # --- Achievements Data ---
        # Fetch all possible achievements to display in the gallery
        context['all_achievements'] = Achievement.objects.all().order_by('title')
        
        # Fetch the achievements this user has earned
        earned_achievements = UserAchievement.objects.filter(user=user)
        
        # Create a dictionary for easy lookup in the template, e.g., {'first_goal': achievement_obj}
        context['user_achievements'] = {ua.achievement.slug: ua for ua in earned_achievements}

        # --- User's Goals Data ---
        # Fetch goals created by the user
        my_goals = Goal.objects.filter(created_by=user)
        # Fetch goals the user is subscribed to
        subscribed_goals = user.subscribed_goals.all()
        # Combine them, remove duplicates, and get the 5 most recent
        context['my_active_goals'] = (my_goals | subscribed_goals).distinct().order_by('-created_at')[:5]
        
        return context

class HomeView(ListView):
    """
    Displays the main home page (index.html).
    The content is now tailored for authenticated vs. unauthenticated users.
    """

    model = GoalCategory
    template_name = "index.html"
    context_object_name = "categories"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Public Data (for all users) ---
        # Add goal count to each category
        categories_with_count = GoalCategory.objects.annotate(
            goal_count=Count("goals", filter=Q(goals__visibility="public"))
        )
        context["categories"] = categories_with_count

        context["top_goals"] = (
            Goal.objects.filter(visibility="public")
            .annotate(num_subscribers=Count("subscribers"))
            .order_by("-num_subscribers")[:10]
        )

        all_streaks = GoalStreak.objects.order_by("user", "-streak_count")
        top_streaks_map = {}
        for streak in all_streaks:
            if streak.user_id not in top_streaks_map:
                top_streaks_map[streak.user_id] = streak

        context["top_streakers"] = sorted(
            top_streaks_map.values(), key=lambda x: x.streak_count, reverse=True
        )[:10]
        print("Top Streakers:", context["top_streakers"])
        # --- Personalized Data (for authenticated users only) ---
        if self.request.user.is_authenticated:
            user = self.request.user
            my_goals = Goal.objects.filter(created_by=user)
            subscribed_goals = user.subscribed_goals.all()
            context["my_personal_goals"] = (
                (my_goals | subscribed_goals).distinct().order_by("-created_at")[:5]
            )

        return context


class RegisterView(View):
    """
    Handles user registration.
    GET: Displays the registration form.
    POST: Processes the form, creates a new user, and logs them in.
    """

    form_class = RegistrationForm
    template_name = "registration/register.html"

    def get(self, request, *args, **kwargs):
        # If user is already authenticated, redirect them to the home page
        if request.user.is_authenticated:
            return redirect("home")
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")
            password = form.cleaned_data.get("password")

            try:
                # Create the user. Username is set to the email for uniqueness.
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                )

                # Log the newly created user in automatically
                login(request, user)
                messages.success(
                    request,
                    f"Xush kelibsiz, {first_name}! Hisobingiz muvaffaqiyatli yaratildi.",
                )

                # Redirect to the home page after successful registration
                return redirect("home")

            except Exception as e:
                # Handle potential, though unlikely, errors during user creation
                messages.error(
                    request,
                    "Hisob yaratishda kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
                )

        # If form is invalid, re-render the page with the form and its errors
        return render(request, self.template_name, {"form": form})


class GoalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Handles the editing of an existing goal.

    - LoginRequiredMixin: Ensures the user is logged in.
    - UserPassesTestMixin: Ensures only the user who created the goal can edit it.
    - UpdateView: Provides the core logic for fetching an object and handling form updates.
    """

    model = Goal
    form_class = GoalForm
    template_name = "goal_form.html"  # Reuses the same form template as the create view
    context_object_name = "goal"

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
        return reverse_lazy(
            "category_detail", kwargs={"slug": self.object.category.slug}
        )

    def get_context_data(self, **kwargs):
        """
        Adds the page title to the context for the template.
        """
        context = super().get_context_data(**kwargs)
        context["pacge_title"] = "Maqsadni Tahrirlash"
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
    template_name = "goal_confirm_delete.html"  # The template you have in the Canvas
    context_object_name = "goal"

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
        messages.success(
            self.request, f"'{self.object.title}' maqsadi muvaffaqiyatli o'chirildi."
        )
        return reverse_lazy("category_detail", kwargs={"slug": category_slug})


from .forms import GoalForm


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = "goal_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request, f"'{form.instance.title}' maqsadi muvaffaqiyatli qo'shildi!"
        )
        form.instance.created_by = self.request.user
        messages.success(
            self.request, f"'{form.instance.title}' maqsadi muvaffaqiyatli qo'shildi!"
        )
        # Yangi maqsad uchun XP qo'shish
        add_xp_and_check_level_up(self.request, 25)
        grant_achievement(
            self.request, "first_goal"
        )  # Birinchi maqsad yutug'ini tekshirish
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "category_detail", kwargs={"slug": self.object.category.slug}
        )


def load_subcategories(request):
    """
    Called via AJAX to load sub-categories based on the selected category.
    """
    category_id = request.GET.get("category_id")
    subcategories = SubCategory.objects.filter(category_id=category_id).values(
        "id", "name"
    )
    return JsonResponse(list(subcategories), safe=False)


class SubscribeToGoalView(LoginRequiredMixin, View):
    """
    Handles a user's request to subscribe or unsubscribe from a goal.
    """

    def post(self, request, *args, **kwargs):
        goal_id = self.kwargs.get("goal_id")
        goal = get_object_or_404(Goal, id=goal_id)

        if goal.subscribers.filter(id=request.user.id).exists():
            # User is already a subscriber, so unsubscribe them
            goal.subscribers.remove(request.user)
            messages.info(
                request, f"Siz '{goal.title}' maqsadidan obunani bekor qildingiz."
            )
        else:
            # User is not a subscriber, so subscribe them
            goal.subscribers.add(request.user)
            messages.success(
                request,
                f"Siz '{goal.title}' maqsadiga muvaffaqiyatli obuna bo'ldingiz!",
            )

        if not goal.subscribers.filter(id=request.user.id).exists():
            goal.subscribers.add(request.user)
            # Obuna bo'lganlik uchun XP qo'shish
            add_xp_and_check_level_up(request, 5)

        return redirect(request.META.get("HTTP_REFERER", reverse_lazy("home")))


class CategoryDetailView(ListView):
    """
    Displays a list of goals within a specific category.
    Includes a filtering system for public and private goals.
    """

    model = Goal
    template_name = "category_detail.html"  # New template
    context_object_name = "goals"
    paginate_by = 12

    def get_queryset(self):
        """
        Filters the goals based on the category and the 'visibility'
        query parameter ('public', 'private', 'all').
        """
        self.category = get_object_or_404(GoalCategory, slug=self.kwargs["slug"])
        user = self.request.user
        visibility_filter = self.request.GET.get(
            "visibility", "public"
        )  # Default to public

        # Start with the base queryset for the current category
        queryset = Goal.objects.filter(category=self.category)

        if visibility_filter == "private":
            if user.is_authenticated:
                # Show only the current user's private goals
                queryset = queryset.filter(created_by=user, visibility="private")
            else:
                # Unauthenticated users can't have private goals
                queryset = queryset.none()
        elif visibility_filter == "my_goals":
            if user.is_authenticated:
                # Show all goals created by the current user (public and private)
                queryset = queryset.filter(created_by=user)
            else:
                queryset = queryset.none()
        else:  # Default to 'public'
            queryset = queryset.filter(visibility="public")

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        """
        Adds the category object and the current filter to the context.
        """
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["active_filter"] = self.request.GET.get("visibility", "public")

        return context


class SubTaskCreateView(LoginRequiredMixin, View):
    """
    AJAX orqali yangi kichik vazifa yaratishni boshqaradi.
    Endi maqsad muallifi YOKI obunachilari vazifa qo'shishi mumkin.
    """

    def post(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal, pk=self.kwargs.get("goal_pk"))

        # YANGILANGAN TEKSHIRUV: Foydalanuvchi muallif yoki obunachimi?
        if not (
            request.user == goal.created_by or request.user in goal.subscribers.all()
        ):
            return JsonResponse(
                {"error": "Faqat obunachilar vazifa qo‘sha oladi."}, status=403
            )

        form = SubTaskForm(request.POST)
        if form.is_valid():
            subtask = form.save(commit=False)
            subtask.goal = goal
            subtask.save()
            return JsonResponse(
                {
                    "status": "ok",
                    "subtask": {
                        "id": subtask.id,
                        "title": subtask.title,
                        "is_completed": subtask.is_completed,
                    },
                    "progress": goal.progress_percentage,
                }
            )
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)


class SubTaskToggleView(LoginRequiredMixin, View):
    """
    AJAX orqali kichik vazifaning 'bajarildi' holatini o'zgartiradi.
    Endi maqsad muallifi YOKI obunachilari holatni o'zgartirishi mumkin.
    """

    def post(self, request, *args, **kwargs):
        subtask = get_object_or_404(SubTask, pk=self.kwargs.get("subtask_pk"))
        goal = subtask.goal

        # YANGILANGAN TEKSHIRUV: Foydalanuvchi muallif yoki obunachimi?
        if not (
            request.user == goal.created_by or request.user in goal.subscribers.all()
        ):
            return JsonResponse(
                {"error": "Faqat obunachilar vazifani belgilay oladi."}, status=403
            )

        subtask.is_completed = not subtask.is_completed
        subtask.save()

        return JsonResponse(
            {
                "status": "ok",
                "is_completed": subtask.is_completed,
                "progress": goal.progress_percentage,
            }
        )


class GoalDetailView(DetailView):
    """
    Handles the display of a single goal with all its related data:
    subscribers, streaks, leaderboard, and chat.
    """

    model = Goal
    template_name = "goal_detail.html"  # The new, final template
    context_object_name = "goal"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goal = self.get_object()
        user = self.request.user

        if self.request.user.is_authenticated:
            context["subtasks"] = goal.subtasks.all()
            context["subtask_form"] = SubTaskForm()
        # --- Basic Goal Data ---
        context["subscribers"] = goal.subscribers.all()
        context["subscribers_count"] = goal.subscribers.count()

        # --- Leaderboard Logic (Database Agnostic) ---
        all_streaks = GoalStreak.objects.filter(goal=goal).order_by("user", "-date")
        latest_streaks_map = {}
        for streak in all_streaks:
            if streak.user_id not in latest_streaks_map:
                latest_streaks_map[streak.user_id] = streak

        leaderboard = sorted(
            latest_streaks_map.values(), key=lambda x: x.streak_count, reverse=True
        )[:10]
        context["leaderboard"] = leaderboard

        # --- Streak, Check-in, and Chat Logic (for authenticated users) ---
        if user.is_authenticated:
            today = timezone.now().date()
            context["has_checked_in_today"] = GoalStreak.objects.filter(
                goal=goal, user=user, date=today
            ).exists()

            # Weekly streak calendar data
            week_days_data = []
            user_streaks_this_week = GoalStreak.objects.filter(
                goal=goal, user=user, date__gte=today - timedelta(days=6)
            ).values_list("date", flat=True)

            for i in range(6, -1, -1):  # Iterate from 6 days ago to today
                day = today - timedelta(days=i)
                week_days_data.append(
                    {
                        "name": day.strftime("%a")[0],
                        "date": day.day,
                        "is_active": day in user_streaks_this_week,
                    }
                )
            context["week_days"] = week_days_data

            # Chat system data
            is_subscribed = user in context["subscribers"] or user == goal.created_by
            context["is_subscribed_to_chat"] = is_subscribed
            if is_subscribed:
                context["chat_messages"] = goal.chat_messages.all().select_related(
                    "user"
                )
                context["message_form"] = MessageForm()

        return context


# --- Supporting AJAX/Action Views ---


class CheckInView(LoginRequiredMixin, View):
    """
    Foydalanuvchining kunlik belgilanish (check-in) mantiqini boshqaradi.
    """
    def post(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal, id=self.kwargs.get('goal_id'))
        user = request.user
        today = timezone.now().date()

        # Foydalanuvchi bugun uchun allaqachon belgilanganligini tekshirish
        if GoalStreak.objects.filter(goal=goal, user=user, date=today).exists():
            messages.warning(request, "Siz bugun uchun allaqachon belgilandingiz!")
            return redirect(goal.get_absolute_url())

        # Yangi seriyani hisoblash
        yesterday = today - timedelta(days=1)
        yesterdays_streak = GoalStreak.objects.filter(goal=goal, user=user, date=yesterday).first()

        new_streak_count = 1
        if yesterdays_streak:
            new_streak_count = yesterdays_streak.streak_count + 1

        # Yangi seriya yozuvini yaratish
        GoalStreak.objects.create(
            goal=goal,
            user=user,
            date=today,
            streak_count=new_streak_count
        )

        # Geymifikatsiya mantiqini ishga tushirish
        add_xp_and_check_level_up(request, 10) # Har bir check-in uchun 10 XP
        if new_streak_count == 7:
            grant_achievement(request, '7_day_streak')
        
        messages.success(request, f"Tabriklaymiz! Sizning seriyangiz: {new_streak_count} kun.")
        return redirect(goal.get_absolute_url())


class PostMessageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal, id=self.kwargs.get("goal_id"))
        if not (
            request.user in goal.subscribers.all() or request.user == goal.created_by
        ):
            return HttpResponseForbidden()
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.goal = goal
            message.user = request.user
            message.save()
            return JsonResponse({"status": "ok"})
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)


class FetchMessagesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        goal = get_object_or_404(Goal, id=self.kwargs.get("goal_id"))
        if not (
            request.user in goal.subscribers.all() or request.user == goal.created_by
        ):
            return HttpResponseForbidden()

        last_ts = request.GET.get("last_timestamp")
        messages_qs = (
            GoalMessage.objects.filter(goal=goal, timestamp__gt=last_ts)
            if last_ts
            else GoalMessage.objects.filter(goal=goal)
        )

        data = [
            {
                "user": msg.user.first_name or msg.user.username,
                "avatar_url": f"https://i.pravatar.cc/150?u={msg.user.username}",
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat(),
                "is_self": msg.user == request.user,
            }
            for msg in messages_qs.select_related("user")
        ]
        return JsonResponse(data, safe=False)
