from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # Import your custom User model

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_approved', 'is_staff')
    list_filter = ('is_approved', 'is_staff')
    search_fields = ('username', 'email')
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)  # ✅ Approve selected users
    approve_users.short_description = "Approve selected users"

# ✅ REGISTER ONLY ONCE, with error handling
if not admin.site.is_registered(User):
    admin.site.register(User, CustomUserAdmin)
