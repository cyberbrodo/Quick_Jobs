from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{10,15}$",
    message="Enter a valid phone number.",
)


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[phone_validator],
    )

    full_name = models.CharField(
        max_length=150,
        blank=True,
    )

    district = models.CharField(
        max_length=100,
        blank=True,
    )

    profile_completed = models.BooleanField(
        default=False,
    )

    # Profile is a new table, so these fields are safe.
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name or self.phone


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Job(models.Model):
    # Old jobs may not have an owner, so temporarily nullable.
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
    )

    shop_name = models.CharField(
        max_length=150,
    )

    title = models.CharField(
        max_length=150,
    )

    # Old jobs may have missing category values.
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="jobs",
        null=True,
        blank=True,
    )

    experience = models.CharField(
        max_length=100,
        default="Fresher",
    )

    work_time = models.CharField(
        max_length=100,
    )

    gender = models.CharField(max_length=20, default="Any")

    education = models.CharField(max_length=50, default="Any")

    age_limit = models.CharField(
        max_length=50,
        blank=True,
    )

    location = models.CharField(
        max_length=100,
    )

    salary = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=15,
        validators=[phone_validator],
    )

    description = models.TextField(
        blank=True,
    )

    is_verified = models.BooleanField(
        default=True,
    )
    owner_name = models.CharField(
        max_length=150,
        blank=True
    )



    # This field was already in the old Job table.
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.shop_name} - {self.title}"


class SavedJob(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class ActivityLog(models.Model):
    LOGIN = "LOGIN"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    JOB_ADDED = "JOB_ADDED"
    JOB_EDITED = "JOB_EDITED"
    JOB_DELETED = "JOB_DELETED"
    JOB_SAVED = "JOB_SAVED"
    JOB_UNSAVED = "JOB_UNSAVED"
    LOGOUT = "LOGOUT"

    ACTION_CHOICES = [
        (LOGIN, "Login"),
        (PROFILE_UPDATED, "Profile Updated"),
        (JOB_ADDED, "Job Added"),
        (JOB_EDITED, "Job Edited"),
        (JOB_DELETED, "Job Deleted"),
        (JOB_SAVED, "Job Saved"),
        (JOB_UNSAVED, "Job Unsaved"),
        (LOGOUT, "Logout"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
    )

    description = models.TextField(
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    # ActivityLog is a new table, so this is safe.
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        username = self.user.username if self.user else "Deleted User"
        return f"{username} - {self.get_action_display()}"