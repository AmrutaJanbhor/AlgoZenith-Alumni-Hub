from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Job
from django.conf import settings
from .forms import JobForm
from django.core.mail import send_mail
from users.models import User  # Import User model

@login_required
def job_list(request):
    """ View all job postings """
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'jobs/job_list.html', {'jobs': jobs})

@login_required
def post_job(request):
    if request.user.role != "alumni":  # Ensure only alumni can post
        return redirect("home1")  # Redirect non-alumni users
    
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user  # Assign the logged-in user
            job.save()
            # Notify all users
            user_emails = User.objects.values_list("email", flat=True)
            send_mail(
                "New Job Posted",
                f"A new job '{job.title}' has been posted by {request.user.username}. Check it out!",
                settings.DEFAULT_FROM_EMAIL,
                user_emails,
                fail_silently=True,
            )
            return redirect("job_list")  # Redirect to job listings
    else:
        form = JobForm()

            


    return render(request, "jobs/post_job.html", {"form": form})
