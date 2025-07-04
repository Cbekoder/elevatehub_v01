from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


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
    """
    Represents a category for goals, e.g., "Sport", "Business".
    Each category has a name, a unique slug for URLs, a color for styling,
    and an icon reference.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya nomi")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    color = models.CharField(max_length=7, help_text="Tailwind CSS rang kodi (masalan, #AFFF6C)", verbose_name="Rang")
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Heroicons uchun belgi nomi (masalan, 'hi-bolt')",
        verbose_name="Belgi"
    )

    class Meta:
        verbose_name = "Maqsad kategoriyasi"
        verbose_name_plural = "Maqsad kategoriyalari"
        ordering = ['name'] # Order categories alphabetically by name

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically generate a slug
        from the category name if it's not already set.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns the string representation of the GoalCategory, which is its name.
        """
        return self.name

    def get_absolute_url(self):
        """
        Returns the URL to access a particular instance of the GoalCategory.
        Used for linking to category detail pages.
        """
        return reverse('category_detail', kwargs={'slug': self.slug})

class Goal(models.Model):
    """
    Represents an individual goal set by a user.
    Each goal has a title, an optional description, a category,
    the user who created it, and a creation timestamp.
    """
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    category = models.ForeignKey(
        GoalCategory,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name="Kategoriya"
    )
    created_by = models.ForeignKey(
        CustomUser, # Use your CustomUser model
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name="Yaratuvchi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")

    class Meta:
        verbose_name = "Maqsad"
        verbose_name_plural = "Maqsadlar"
        ordering = ['-created_at'] # Order goals by creation date, newest first

    def __str__(self):
        """
        Returns the string representation of the Goal, which is its title.
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns the URL to access a particular instance of the Goal.
        For now, it redirects to its category detail page. You might
        want to create a specific goal detail URL later.
        """
        return reverse('category_detail', kwargs={'slug': self.category.slug})
        # If you later create a goal detail view, you might change this to:
        # return reverse('goal_detail', kwargs={'pk': self.pk})
