from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from elevatehub import settings


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    This allows for easy customization of the User model in the future.
    For now, it behaves exactly like the default User model,
    but you can add new fields (e.g., phone_number, bio, profile_picture) here.
    """

    # Example of adding a new field (uncomment if you want to add it)
    # phone_number = models.CharField(max_length=15, blank=True, null=True)

    # You can also override existing fields if needed, e.g., to make email unique
    email = models.EmailField(unique=True, blank=False, null=False)

    def __str__(self):
        """
        Returns the string representation of the user.
        Prioritizes username, then email if username is empty, otherwise a default.
        """
        if self.username:
            return self.username
        elif self.email:
            return self.email
        return f"User {self.pk}"

    class Meta:
        """
        Meta options for the CustomUser model.
        """

        verbose_name = "User"
        verbose_name_plural = "Users"
        # You can add other meta options here, like ordering
        # ordering = ['username']


class GoalCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    color = models.CharField(max_length=20, default="#e0e7ff", verbose_name="Rangi")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ikona")

    class Meta:
        verbose_name = "Maqsad Yo'nalishi"
        verbose_name_plural = "Maqsad Yo'nalishlari"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """
    Represents an "Ichki yo'nalish" within a main GoalCategory.
    """

    category = models.ForeignKey(
        GoalCategory, on_delete=models.CASCADE, related_name="subcategories"
    )
    name = models.CharField(max_length=100, verbose_name="Nomi")

    class Meta:
        verbose_name = "Ichki Yo'nalish"
        verbose_name_plural = "Ichki Yo'nalishlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Goal(models.Model):
    VISIBILITY_CHOICES = [("public", "Ommaviy"), ("private", "Shaxsiy")]
    DURATION_CHOICES = [(7, "7 kun"), (14, "14 kun"), (21, "21 kun"), (28, "28 kun")]
    title = models.CharField(max_length=200, verbose_name="Maqsad Nomi")
    description = models.TextField(verbose_name="Izoh")
    category = models.ForeignKey(
        GoalCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="goals",
        verbose_name="Yo'nalishi",
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Ichki Yo'nalish",
    )
    duration = models.IntegerField(choices=DURATION_CHOICES, verbose_name="Davomiyligi")
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="public",
        verbose_name="Ko'rinishi",
    )
    phone_number = models.CharField(
        max_length=20, blank=True, verbose_name="Telefon Raqam"
    )
    telegram_username = models.CharField(
        max_length=100, blank=True, verbose_name="Telegram User"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_goals"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="subscribed_goals", blank=True
    )

    def get_absolute_url(self):
        return reverse("goal_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        """
        Maqsadning bajarilish foizini hisoblaydi.
        """
        subtasks = self.subtasks.all()
        if not subtasks.exists():
            return 0
        completed_count = subtasks.filter(is_completed=True).count()
        return int((completed_count / subtasks.count()) * 100)


class SubTask(models.Model):
    """
    Katta maqsad uchun kichik vazifani ifodalaydi.
    """

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=255, verbose_name="Vazifa nomi")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title


class GoalStreak(models.Model):
    """
    Tracks a user's daily check-in streak for a specific goal.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="streaks"
    )
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="streaks")
    date = models.DateField(default=timezone.now)
    streak_count = models.IntegerField(default=1)

    class Meta:
        # Ensures a user can only check in once per day for a specific goal
        unique_together = ("user", "goal", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username}'s streak for '{self.goal.title}' on {self.date}"


class GoalMessage(models.Model):
    """
    Represents a single message within a goal's chat room.
    """

    goal = models.ForeignKey(
        "Goal", on_delete=models.CASCADE, related_name="chat_messages"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Message by {self.user.username} on {self.goal.title}"
