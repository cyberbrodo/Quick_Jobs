import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import (Category, Job, SavedJob,Profile,ActivityLog,)

def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def create_activity(request, action, description=""):
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        description=description,
        ip_address=get_client_ip(request),
    )


# =========================================================
# FIREBASE PHONE LOGIN PAGE
# =========================================================

def send_otp(request):
    if request.user.is_authenticated:
        return redirect("home")

    return render(request, "email.html")


# =========================================================
# FIREBASE LOGIN → DJANGO SESSION
# NOTE: This is the simple Option 1 flow.
# Later Firebase ID token backend verification add cheyyanam.
# =========================================================

def firebase_login(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required",
            },
            status=405,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid request data",
            },
            status=400,
        )

    phone = data.get("phone", "").strip()

    if not phone:
        return JsonResponse(
            {
                "success": False,
                "message": "Phone number missing",
            },
            status=400,
        )

    if not phone.startswith("+91") or len(phone) != 13:
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid phone number",
            },
            status=400,
        )

    username = phone.replace("+", "")

    user, user_created = User.objects.get_or_create(
        username=username
    )

    profile, profile_created = Profile.objects.get_or_create(
        user=user,
        defaults={
            "phone": phone,
            "full_name": user.first_name or "",
        },
    )

    if profile.phone != phone:
        profile.phone = phone
        profile.save(update_fields=["phone"])

    # Old user-il Profile name undengil User.first_name sync cheyyuka
    if profile.full_name and user.first_name != profile.full_name:
        user.first_name = profile.full_name
        user.save(update_fields=["first_name"])

    # User.first_name undengil Profile full_name sync cheyyuka
    if user.first_name and not profile.full_name:
        profile.full_name = user.first_name
        profile.profile_completed = True
        profile.save(
            update_fields=[
                "full_name",
                "profile_completed",
            ]
        )

    login(request, user)

    create_activity(
        request,
        "LOGIN",
        f"User logged in using phone {phone}",
    )

    if (
        user_created
        or profile_created
        or not profile.profile_completed
        or not profile.full_name.strip()
    ):
        redirect_url = reverse("complete_profile")
    else:
        redirect_url = reverse("home")

    return JsonResponse(
        {
            "success": True,
            "redirect_url": redirect_url,
        }
    )
# =========================================================
# COMPLETE PROFILE
# =========================================================

@login_required(login_url="login")
def complete_profile(request):
    phone = f"+{request.user.username}"

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "phone": phone,
        },
    )

    if not profile.phone:
        profile.phone = phone
        profile.save(update_fields=["phone"])

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        district = request.POST.get("district", "").strip()

        if not name:
            messages.error(
                request,
                "Please enter your name",
            )
            return render(
                request,
                "complete_profile.html",
                {
                    "profile": profile,
                },
            )

        # Django User-il name save
        request.user.first_name = name
        request.user.save(update_fields=["first_name"])

        # Profile-il same name save
        profile.full_name = name
        profile.district = district
        profile.profile_completed = True
        profile.save(
            update_fields=[
                "full_name",
                "district",
                "profile_completed",
                "updated_at",
            ]
        )

        create_activity(
            request,
            "PROFILE_UPDATED",
            f"Profile completed by {name}",
        )

        messages.success(
            request,
            "Profile completed successfully",
        )

        return redirect("home")

    # Existing User name Profile-il display cheyyan
    if not profile.full_name and request.user.first_name:
        profile.full_name = request.user.first_name

    return render(
        request,
        "complete_profile.html",
        {
            "profile": profile,
        },
    )
# =========================================================
# HOME + SEARCH + FILTER
# =========================================================

def home(request):
    jobs = (
        Job.objects
        .filter(is_verified=True)
        .select_related("category", "owner")
        .order_by("-id")
    )

    categories = Category.objects.all().order_by("name")

    q = request.GET.get("q", "").strip()
    place = request.GET.get("place", "").strip()
    category_id = request.GET.get("category", "").strip()

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q)
            | Q(shop_name__icontains=q)
            | Q(description__icontains=q)
            | Q(category__name__icontains=q)
        )

    if place:
        jobs = jobs.filter(location__icontains=place)

    if category_id.isdigit():
        jobs = jobs.filter(category_id=int(category_id))

    saved_job_ids = set()

    if request.user.is_authenticated:
        saved_job_ids = set(
            SavedJob.objects.filter(
                user=request.user
            ).values_list("job_id", flat=True)
        )

    return render(
        request,
        "home.html",
        {
            "jobs": jobs,
            "categories": categories,
            "saved_job_ids": saved_job_ids,
        },
    )


# =========================================================
# PROFILE
# =========================================================

@login_required(login_url="login")
def profile(request):
    jobs = (
        Job.objects
        .filter(owner=request.user)
        .select_related("category")
        .order_by("-id")
    )

    return render(
        request,
        "profile.html",
        {
            "jobs": jobs,
        },
    )


# =========================================================
# ADD JOB
# =========================================================

@login_required(login_url="login")
def add_job(request):
    profile = Profile.objects.filter(
        user=request.user
    ).first()

    owner_name = request.user.first_name.strip()

    if profile and profile.full_name.strip():
        owner_name = profile.full_name.strip()

    if not owner_name:
        return redirect("complete_profile")

    if request.method == "POST":
        category_name = request.POST.get(
            "category", ""
        ).strip()

        shop_name = request.POST.get(
            "shop_name", ""
        ).strip()

        title = request.POST.get(
            "title", ""
        ).strip()

        experience = (
            request.POST.get(
                "experience", ""
            ).strip()
            or "Fresher"
        )

        work_time = request.POST.get(
            "work_time", ""
        ).strip()

        location = request.POST.get(
            "location", ""
        ).strip()

        salary = request.POST.get(
            "salary", ""
        ).strip()

        phone = request.POST.get(
            "phone", ""
        ).strip()

        age_limit = request.POST.get(
            "age_limit", ""
        ).strip()

        description = request.POST.get(
            "description", ""
        ).strip()

        if not all([
            category_name,
            shop_name,
            title,
            work_time,
            location,
            salary,
            phone,
        ]):
            messages.error(
                request,
                "Please fill all required fields",
            )

            return render(
                request,
                "addjob.html",
                {
                    "form_data": request.POST,
                    "owner_name": owner_name,
                },
            )

        category, _ = Category.objects.get_or_create(
            name__iexact=category_name,
            defaults={
                "name": category_name.title(),
            },
        )

        job = Job.objects.create(
            owner=request.user,
            shop_name=shop_name,
            title=title,
            category=category,
            experience=experience,
            work_time=work_time,
            age_limit=age_limit,
            location=location,
            salary=salary,
            owner_name=owner_name,
            phone=phone,
            description=description,
            is_verified=True,
        )

        create_activity(
            request,
            "JOB_ADDED",
            f"Added job #{job.id}: {job.title}",
        )

        messages.success(
            request,
            "Job added successfully",
        )

        return redirect("home")

    return render(
        request,
        "addjob.html",
        {
            "owner_name": owner_name,
        },
    )
#=========================================================
# EDIT JOB
# =========================================================

@login_required(login_url="login")
def edit_job(request, id):
    job = get_object_or_404(
        Job,
        id=id,
        owner=request.user,
    )

    if request.method == "POST":
        category_name = request.POST.get(
            "category", ""
        ).strip()

        if not category_name:
            messages.error(request, "Category is required")
            return redirect("edit_job", id=job.id)

        category, _ = Category.objects.get_or_create(
            name__iexact=category_name,
            defaults={"name": category_name.title()},
        )

        job.shop_name = request.POST.get(
            "shop_name", ""
        ).strip()

        job.title = request.POST.get(
            "title", ""
        ).strip()

        job.category = category

        job.experience = (
            request.POST.get("experience", "").strip()
            or "Fresher"
        )

        job.work_time = request.POST.get(
            "work_time", ""
        ).strip()

        job.age_limit = request.POST.get(
            "age_limit", ""
        ).strip()

        job.location = request.POST.get(
            "location", ""
        ).strip()

        job.salary = request.POST.get(
            "salary", ""
        ).strip()

        job.phone = request.POST.get(
            "phone", ""
        ).strip()

        job.description = request.POST.get(
            "description", ""
        ).strip()

        if request.FILES.get("logo"):
            job.logo = request.FILES["logo"]

        # Edit cheythal home-il ninn disappear aakaruth.
        job.is_verified = True

        job.save()

        messages.success(request, "Job updated successfully")
        return redirect("profile")

    return render(
        request,
        "addjob.html",
        {
            "job": job,
        },
    )


# =========================================================
# DELETE JOB
# =========================================================

@login_required(login_url="login")
def delete_job(request, job_id):
    job = get_object_or_404(
        Job,
        id=job_id,
        owner=request.user,
    )

    job.delete()

    messages.success(
        request,
        "Job deleted successfully.",
    )

    return redirect("profile")


# =========================================================
# SAVE / UNSAVE JOB
# =========================================================

@login_required(login_url="login")
def save_job(request, id):
    job = get_object_or_404(
        Job,
        id=id,
        is_verified=True,
    )

    saved_job, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job,
    )

    if created:
        messages.success(request, "Job saved")
    else:
        saved_job.delete()
        messages.info(request, "Job removed from saved jobs")

    next_url = request.GET.get("next")

    if next_url and next_url.startswith("/"):
        return redirect(next_url)

    return redirect("home")


@login_required(login_url="login")
def saved_jobs(request):
    saved = (
        SavedJob.objects
        .filter(
            user=request.user,
            job__is_verified=True,
        )
        .select_related("job", "job__category")
        .order_by("-id")
    )

    return render(
        request,
        "saved.html",
        {
            "saved": saved,
        },
    )


@login_required(login_url="login")
def remove_saved_job(request, id):
    saved_job = get_object_or_404(
        SavedJob,
        id=id,
        user=request.user,
    )

    saved_job.delete()
    messages.info(request, "Job removed from saved jobs")

    return redirect("saved_jobs")


# =========================================================
# JOB DETAILS
# =========================================================

def job_details(request, id):
    job = get_object_or_404(
        Job.objects.select_related(
            "category",
            "owner",
        ),
        id=id,
        is_verified=True,
    )

    return render(
        request,
        "job_details.html",
        {
            "job": job,
        },
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required(login_url="login")
def logout_user(request):
    logout(request)
    return redirect("home")