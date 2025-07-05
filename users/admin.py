from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import (
    CustomUser, Profile,
    Achievement, UserAchievement,
    GoalCategory, SubCategory,
    Goal, SubTask, GoalStreak, GoalMessage
)
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    # If you add custom fields to CustomUser, you'll need to update
    # fieldsets and add_fieldsets here to make them visible in the admin.

    # Example: Adding 'email' to fieldsets (it's already there by default,
    # but this shows how to customize)
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('email',)}), # Add 'email' to a new section or existing
    #     # If you added 'phone_number' to CustomUser:
    #     # ('Contact Info', {'fields': ('phone_number',)}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('email',)}),
    
    # )

    list_display = UserAdmin.list_display + ('email',) # Add email to list view
    search_fields = ('username', 'email', 'first_name', 'last_name') # Add email to search



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'xp', 'level', 'coins')
    search_fields = ('user__username',)
    readonly_fields = ('user',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'xp_reward', 'coin_reward')
    search_fields = ('title', 'slug')
    prepopulated_fields = {"slug": ("title",)}


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    search_fields = ('user__username', 'achievement__title')
    list_filter = ('earned_at',)


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'icon')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'sub_category', 'duration', 'visibility', 'created_by', 'created_at')
    list_filter = ('visibility', 'duration', 'category', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    date_hierarchy = 'created_at'


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'goal', 'is_completed', 'created_at')
    list_filter = ('is_completed',)
    search_fields = ('title', 'goal__title')
    date_hierarchy = 'created_at'


@admin.register(GoalStreak)
class GoalStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'date', 'streak_count')
    search_fields = ('user__username', 'goal__title')
    list_filter = ('date',)
    date_hierarchy = 'date'


@admin.register(GoalMessage)
class GoalMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal', 'timestamp')
    search_fields = ('user__username', 'goal__title', 'message')
    date_hierarchy = 'timestamp'

