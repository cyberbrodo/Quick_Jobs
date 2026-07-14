from django.contrib import admin
from .models import Job, SavedJob, Category



from django.contrib import admin
from django.contrib.auth.models import User

from .models import (
    Profile,
    Category,
    Job,
    SavedJob,
    ActivityLog,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "phone",
        "user",
        "profile_completed",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "full_name",
        "phone",
        "user__username",
    )

    list_filter = (
        "profile_completed",
        "created_at",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

    search_fields = (
        "name",
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "shop_name",
        "owner",
        "category",
        "location",
        "salary",
        "is_verified",
        "created_at",
    )

    search_fields = (
        "title",
        "shop_name",
        "location",
        "phone",
        "owner__username",
        "owner__first_name",
    )

    list_filter = (
        "is_verified",
        "category",
        "created_at",
    )

    list_editable = (
        "is_verified",
    )


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job")

    search_fields = (
        "user__username",
        "job__title",
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "description",
        "ip_address",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "description",
        "ip_address",
    )

    list_filter = (
        "action",
        "created_at",
    )

    readonly_fields = (
        "user",
        "action",
        "description",
        "ip_address",
        "created_at",
    )