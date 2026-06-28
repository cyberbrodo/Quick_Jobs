from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shop_name = models.CharField(max_length=150)
    title = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    experience = models.CharField(max_length=100, default="Fresher")
    work_time = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="job_logos", blank=True, null=True)
    age_limit = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100, blank=True)
    owner_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15)
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


