from django.shortcuts import render
from django.contrib.auth.models import User
from alumni.models import Alumni
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .models import Connection

def users_directory(request):
    User = get_user_model()  
    query = request.GET.get('q')  # Get search query from request

    # Fetch all users along with their alumni profiles
    users = User.objects.all().select_related('alumni_profile')

    if query:
        users = users.filter(username__icontains=query)  # Filter users based on query

    return render(request, 'alumni/users_directory.html', {'users': users, 'query': query})


def send_connection_request(request, user_id):
    if request.user.is_authenticated:
        recipient = get_object_or_404(User, id=user_id)
        if request.user != recipient:
            Connection.objects.get_or_create(sender=request.user, receiver=recipient, status='pending')
        return redirect('users_directory')
    else:
        return redirect('login')
def connection_requests(request):
    # Fetch all incoming connection requests for the logged-in user
    incoming_requests = Connection.objects.filter(receiver=request.user, status='pending')
    return render(request, 'users/connection_requests.html', {'incoming_requests': incoming_requests})
