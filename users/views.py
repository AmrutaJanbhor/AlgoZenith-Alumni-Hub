from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm, EducationForm, WorkExperienceForm
from .models import Education, WorkExperience
from alumni.models import Alumni
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from users.models import Profile
from django.db import models
from events.models import Event
from django.db.models import Q
from .models import ConnectionRequest
from django.contrib.auth import get_user_model
from users.decorators import approval_required
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

def home(request):
    return render(request, 'users/home.html')

# Home Page View
def home1(request):
    events = Event.objects.all()
    
    return render(request, 'users/home1.html',{'user':request.user,'events':events})

# Register View
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.role = form.cleaned_data["role"]
            user.is_approved = False  # 🚨 Require admin approval
            user.save()

            # ✅ Automatically create an Alumni entry if role is 'alumni'
            if user.role == "alumni":
                Alumni.objects.create(user=user, name=user.username, email=user.email)

            # ❌ Prevent automatic login
            messages.success(request, "Your account has been created and is pending admin approval.")

            # ✅ Notify admin (Optional)
            admin_email = settings.ADMIN_EMAIL  # Add in settings.py
            send_mail(
                "New User Registration - Approval Needed",
                f"A new user {user.username} has registered and needs approval.",
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                fail_silently=True,
            )

            return redirect("login")  # Redirect to login page (without login)

    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})    
# Login View
def custom_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_approved:
                login(request, user)
                return redirect("home1")  # Redirect to homepage
            else:
                messages.error(request, "Your account is pending admin approval.")
                return redirect("login")  # Stay on login page
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    
    return render(request, "users/login.html")
#decorators view
@login_required
@approval_required
def dashboard(request):
    return render(request, "users/dashboard.html")

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')  

# Profile View
@login_required
def profile(request, username):
    try:
        profile = Profile.objects.select_related('user').get(user__username=username)
    except Profile.DoesNotExist:
        messages.error(request, "Profile not found!")
        return redirect('home')  # Redirect to home if profile doesn't exist

    user = profile.user

    # Get all accepted connections
    connections = Connection.objects.filter(
        models.Q(from_user=user, status='accepted') |
        models.Q(to_user=user, status='accepted')
    ).select_related('from_user', 'to_user')

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=user.username)
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'users/profile.html', {
        'profile': profile,
        'form': form,
        'connections': connections,
    })


# Add Education
@login_required
def add_education(request):
    print("add_education view accessed")  # Debugging
    if request.method == "POST":
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            return redirect('profile')
    else:
        form = EducationForm()
    return render(request, 'users/add_education.html', {'form': form})


# Add Work Experience
@login_required
def add_experience(request):
    if request.method == "POST":
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.user = request.user
            experience.save()
            return redirect('profile')  
    else:
        form = WorkExperienceForm()
    return render(request, 'users/add_experience.html', {'form': form})




@login_required
def edit_bio(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        profile.bio = new_bio
        profile.save()
        messages.success(request, 'Bio updated successfully!')
        return redirect('profile', user_id=request.user.id)
    return render(request, 'users/edit_bio.html', {'profile': profile})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, ConnectionRequest, Connection

@login_required
def send_request(request, receiver_id):
    """Send a connection request."""
    receiver = get_object_or_404(User, id=receiver_id)

    if request.user == receiver:
        messages.error(request, "You cannot connect with yourself.")
        return redirect('profile', user_id=receiver.id)

    # Check for existing connections or pending requests
    if Connection.objects.filter(
        Q(from_user=request.user, to_user=receiver) | 
        Q(from_user=receiver, to_user=request.user)
    ).exists():
        messages.warning(request, "You are already connected with this user.")
        return redirect('profile', user_id=receiver.id)

    if ConnectionRequest.objects.filter(sender=request.user, receiver=receiver, status='pending').exists():
        messages.warning(request, "Connection request already sent.")
        return redirect('profile', user_id=receiver.id)

    # Create a new connection request
    ConnectionRequest.objects.create(sender=request.user, receiver=receiver, status='pending')
    messages.success(request, f"Connection request sent to {receiver.username}.")
    return redirect('view_requests')


@login_required
def view_requests(request):
    """View incoming connection requests."""
    pending_requests = ConnectionRequest.objects.filter(receiver=request.user, status='pending')
    return render(request, 'users/view_requests.html', {'pending_requests': pending_requests})


@login_required
def accept_request(request, request_id):
    """Accept a connection request."""
    connection = get_object_or_404(Connection, id=request_id, to_user=request.user)
    connection.status = 'accepted'
    connection.save()
    return redirect('connection_requests')



@login_required
def reject_request(request, request_id):
    """Reject a connection request."""
    connection = get_object_or_404(Connection, id=request_id, to_user=request.user)
    connection.delete()
    return redirect('connection_requests')


def connection_requests(request):
    # Example logic for fetching pending connection requests
    pending_requests = Connection.objects.filter(to_user=request.user, status='pending')
    return render(request, 'users/connection_requests.html', {'pending_requests': pending_requests})

@login_required
def accept_connection(request, connection_id):
    connection = get_object_or_404(Connection, id=connection_id, to_user=request.user)
    if connection.status == 'pending':
        connection.status = 'accepted'
        connection.save()
    return redirect('connection_requests')

@login_required
def reject_connection(request, connection_id):
    connection = get_object_or_404(Connection, id=connection_id, to_user=request.user)
    if connection.status == 'pending':
        connection.status = 'rejected'
        connection.save()
    return redirect('connection_requests')

@login_required
def connection_requests(request):
    """Show all pending connection requests for the logged-in user."""
    pending_requests = Connection.objects.filter(to_user=request.user, status='pending')
    return render(request, 'users/connection_requests.html', {'pending_requests': pending_requests})



def send_connection_request(request, username):
    to_user = get_object_or_404(User, username=username)
    from_user = request.user

    # Check if a request already exists
    if not Connection.objects.filter(from_user=from_user, to_user=to_user).exists():
        Connection.objects.create(from_user=from_user, to_user=to_user, status='pending')

    return redirect('profile', username=username)

@login_required
def my_connections(request):
    """Show all accepted connections for the logged-in user."""
    connections = Connection.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    ).distinct()

    unique_connections = set()
    filtered_connections = []

    for connection in connections:
        user_pair = tuple(sorted([connection.from_user.id, connection.to_user.id]))  # Sort to avoid duplicates
        if user_pair not in unique_connections:
            unique_connections.add(user_pair)
            filtered_connections.append(connection)

    return render(request, 'users/my_connections.html', {'connections': filtered_connections})

@login_required
def view_connections(request, user_id):
    """Show accepted connections for the logged-in user."""
    connections = Connection.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    ).distinct()

    unique_connections = set()
    filtered_connections = []

    for connection in connections:
        user_pair = tuple(sorted([connection.from_user.id, connection.to_user.id]))  # Sort to avoid duplicates
        if user_pair not in unique_connections:
            unique_connections.add(user_pair)
            filtered_connections.append(connection)

    return render(request, 'users/connections.html', {'connections': filtered_connections})

@approval_required
def some_view(request):
    ...