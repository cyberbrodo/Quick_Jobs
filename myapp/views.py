import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q

from .models import Job, SavedJob, Category



def send_otp(request):
    if request.method == "POST":
        email = request.POST.get('email')
        otp = str(random.randint(100000, 999999))

        request.session['otp'] = otp
        request.session['email'] = email

        from django.conf import settings

        try:
            send_mail(
                "Your OTP Code",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print("EMAIL ERROR:", e)
            messages.error(request, "OTP send failed. Try again later.")
            return redirect("login")

        return redirect("otp")

    return render(request, "email.html")


def verify_otp(request):
    if request.method == "POST":
        otp = (
            request.POST.get('otp1', '') +
            request.POST.get('otp2', '') +
            request.POST.get('otp3', '') +
            request.POST.get('otp4', '') +
            request.POST.get('otp5', '') +
            request.POST.get('otp6', '')
        )

        saved_otp = request.session.get('otp')
        email = request.session.get('email')

        if otp == saved_otp and email:
            username = email.split("@")[0]

            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email}
            )

            login(request, user)

            request.session.pop('otp', None)
            request.session.pop('email', None)

            messages.success(request, "Login successful!")
            return redirect("home")

        messages.error(request, "Invalid OTP. try again.")
        return redirect("otp")

    return render(request, "otp.html")



def home(request):
    jobs = Job.objects.filter(is_verified=True).order_by("-id")
    categories = Category.objects.all()

    q = request.GET.get("q", "").strip()
    place = request.GET.get("place", "").strip()
    category = request.GET.get("category", "").strip()

    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(shop_name__icontains=q) |
            Q(description__icontains=q)
        )

    if place:
        jobs = jobs.filter(location__icontains=place)



    saved_job_ids = []

    if request.user.is_authenticated:
        saved_job_ids = SavedJob.objects.filter(
            user=request.user
        ).values_list("job_id", flat=True)

    return render(request, "home.html", {
        "jobs": jobs,
        "categories": categories,
        "saved_job_ids": saved_job_ids,
    })


@login_required(login_url="login")
def profile(request):
    jobs = Job.objects.filter(owner=request.user).order_by("-id")
    return render(request, "profile.html", {"jobs": jobs})


@login_required(login_url="login")
def add_job(request):
    if request.method == "POST":
        category_name = request.POST.get("category", "").strip()

        category, created = Category.objects.get_or_create(
            name=category_name
        )
        job = Job.objects.create(
            owner=request.user,
            shop_name=request.POST.get("shop_name"),
            title=request.POST.get("title"),
            category=category,
            experience=request.POST.get("experience") or "Fresher",
            work_time=request.POST.get("work_time"),
            logo=request.FILES.get("logo"),
            age_limit=request.POST.get("age_limit"),
            location=request.POST.get("location"),
            salary=request.POST.get("salary"),
            owner_name=request.user.username,
            owner_email=request.user.email,
            phone=request.POST.get("phone"),
            description=request.POST.get("description"),
            is_verified=True,
        )

        users_emails = User.objects.exclude(email="").exclude(
            id=request.user.id
        ).values_list("email", flat=True)

        if users_emails:
            send_mail(
                "New Job Submitted on QuickJobs",
                f"""
New job submitted on QuickJobs.

Shop: {job.shop_name}
Job: {job.title}
Category: {job.category.name}
Location: {job.location}
Salary: {job.salary}

Note: This job will be visible after admin approval.
""",
                settings.EMAIL_HOST_USER,
                list(users_emails),
                fail_silently=True,
            )

        return redirect("home")

    return render(request, "addjob.html")


@login_required(login_url="login")
def save_job(request, id):
    job = get_object_or_404(Job, id=id)

    saved, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )

    if not created:
        saved.delete()

    return redirect("home")


@login_required(login_url="login")
def saved_jobs(request):
    saved = SavedJob.objects.filter(user=request.user).order_by("-id")
    return render(request, "saved.html", {"saved": saved})


@login_required(login_url="login")
def remove_saved_job(request, id):
    saved_job = get_object_or_404(SavedJob, id=id, user=request.user)
    saved_job.delete()
    return redirect("saved_jobs")


@login_required(login_url="login")
def edit_job(request, id):
    job = get_object_or_404(Job, id=id, owner=request.user)

    if request.method == "POST":
        category_name = request.POST.get("category", "").strip()

        category, created = Category.objects.get_or_create(
            name=category_name
        )

        job.shop_name = request.POST.get("shop_name")
        job.title = request.POST.get("title")
        job.category = category
        job.experience = request.POST.get("experience") or "Fresher"
        job.work_time = request.POST.get("work_time")
        job.age_limit = request.POST.get("age_limit")
        job.location = request.POST.get("location")
        job.salary = request.POST.get("salary")
        job.phone = request.POST.get("phone")
        job.description = request.POST.get("description")
        job.is_verified = False

        if request.FILES.get("logo"):
            job.logo = request.FILES.get("logo")

        job.save()
        return redirect("profile")

    return render(request, "addjob.html", {"job": job})


@login_required(login_url="login")
def delete_job(request, id):
    job = get_object_or_404(Job, id=id, owner=request.user)
    job.delete()
    return redirect("profile")


def logout_user(request):
    logout(request)
    return redirect("home")


def job_details(request, id):
    job = get_object_or_404(Job, id=id, is_verified=True)
    return render(request, "job_details.html", {"job": job})