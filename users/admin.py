from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

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
