# core/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from users.models import GoalCategory # Assuming GoalCategory is in core.models

class Command(BaseCommand):
    help = 'Populates the database with initial GoalCategory data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Seeding GoalCategory data...'))

        # Optional: Clear existing data before seeding
        GoalCategory.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing GoalCategory data.'))

        categories_data = [
            {'name': "Shaxsiy Rivojlanish", 'color': "#e0e7ff", 'icon': "fa-solid fa-person-walking"},
            {'name': "Sog'liq va Fitness", 'color': "#d1e7dd", 'icon': "fa-solid fa-heart-pulse"},
            {'name': "Moliyaviy Maqsadlar", 'color': "#fff3cd", 'icon': "fa-solid fa-sack-dollar"},
            {'name': "Karyera va Ish", 'color': "#f8d7da", 'icon': "fa-solid fa-briefcase"},
            {'name': "Ta'lim", 'color': "#cff4fc", 'icon': "fa-solid fa-book"},
            {'name': "Oilaviy Maqsadlar", 'color': "#e2e3e5", 'icon': "fa-solid fa-house-user"},
            {'name': "Ijtimoiy Maqsadlar", 'color': "#cfe2ff", 'icon': "fa-solid fa-people-group"},
            {'name': "Ijodkorlik va Xobbi", 'color': "#dae5ed", 'icon': "fa-solid fa-lightbulb"},
        ]

        for data in categories_data:
            GoalCategory.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"Created category: {data['name']}"))

        self.stdout.write(self.style.SUCCESS('GoalCategory seeding completed successfully!'))