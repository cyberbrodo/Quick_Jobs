from django.contrib import admin
from .models import Job, SavedJob, Category

admin.site.register(Job)
admin.site.register(SavedJob)
admin.site.register(Category)