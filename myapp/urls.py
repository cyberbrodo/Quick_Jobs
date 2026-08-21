"""
URL configuration for mypro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path("", views.home, name="home"),

    path("login/", views.send_otp, name="login"),
    path("firebase-login/", views.firebase_login, name="firebase_login"),
    path("logout/", views.logout_user, name="logout_user"),

    path("profile/", views.profile, name="profile"),

    path("add-job/", views.add_job, name="add_job"),
    path("edit-job/<int:id>/", views.edit_job, name="edit_job"),
    path("delete-job/<int:job_id>/",views.delete_job,name="delete_job"),

    path("saved-jobs/", views.saved_jobs, name="saved_jobs"),
    path("login/", views.send_otp, name="login"),
    path("save-job/<int:id>/", views.save_job, name="save_job"),
    path("remove-saved-job/<int:id>/", views.remove_saved_job, name="remove_saved_job"),
path("job/<int:id>/", views.job_details, name="job_details"),
path("complete-profile/", views.complete_profile, name="complete_profile"),
path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),

    # path("about/", views.about, name="about"),
    #
    path("terms/", views.terms, name="terms"),
    #
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    #
    # path("report-job/", views.report_job, name="report_job"),
     path("save-subscription/",views.save_push_subscription,name="save_subscription",),
# path("sw.js",TemplateView.as_view(template_name="sw.js",content_type="application/javascript"),


path("sw.js", views.service_worker, name="service_worker"),
path("all-jobs/", views.all_jobs, name="all_jobs"),
path(
    "add-review/",
    views.add_review,
    name="add_review"
),

]