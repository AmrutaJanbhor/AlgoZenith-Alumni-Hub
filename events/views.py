from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Event,EventRegistration
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from django.contrib import messages
from .forms import EventForm

from django.shortcuts import get_object_or_404



@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Assign current user as creator
            event.save()

             # Notify all users
            user_emails = User.objects.values_list("email", flat=True)
            send_mail(
                "New Event Created",
                f"A new event '{event.title}' has been created by {request.user.username}. Join now!",
                settings.DEFAULT_FROM_EMAIL,
                user_emails,
                fail_silently=True,
            )
            return redirect('event_list')  # Redirect to event listings page
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def event_list(request):
    category = request.GET.get('category', '')  # Get category from URL query params
    events = Event.objects.all().order_by('date')  # Fetch all events sorted by date

    if category:  # If a category is selected, filter events
        events = events.filter(category=category)

    return render(request, 'events/event_list.html', {
        'events': events,
        'selected_category': category  # Pass selected category to template
    })


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        return render(request, 'events/event_detail.html', {'event': event, 'error': 'You are already registered for this event.'})
    
    # Register the user for the event
    EventRegistration.objects.create(event=event, user=request.user)
    return redirect('event_detail', event_id=event.id)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    attendees = EventRegistration.objects.filter(event=event).select_related('user')
    return render(request, 'events/event_detail.html', {'event': event, 'attendees': attendees})
