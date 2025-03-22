from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import  Message,Room
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from users.models import Connection,User

User = get_user_model()


@login_required
@login_required
def chat_list(request):
    user = request.user

    # Get connected user IDs (only accepted connections)
    sent_connections = Connection.objects.filter(from_user=user, status="accepted").values_list("to_user", flat=True)
    received_connections = Connection.objects.filter(to_user=user, status="accepted").values_list("from_user", flat=True)

    # Combine both querysets into a list of unique user IDs
    connected_user_ids = list(sent_connections) + list(received_connections)

    # Get actual user objects
    connected_users = User.objects.filter(id__in=connected_user_ids)

    return render(request, "chat/chat_list.html", {"connected_users": connected_users})


@login_required
def chat_room(request, user_id):
    """Display chat room between the logged-in user and another user."""
    other_user = get_object_or_404(User, id=user_id)

    # Ensure room exists or create a new one
    room_name = f"chat_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"
    room, created = Room.objects.get_or_create(name=room_name)

    # Fetch messages for this room
    messages = Message.objects.filter(room=room).order_by("timestamp")

    return render(request, "chat/chat_room.html", {
        "room": room,
        "messages": messages,
        "other_user": other_user
    })




@login_required
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("content")
        room_id = request.POST.get("room_id")

        if not content or not room_id:
            return JsonResponse({"error": "Missing content or room ID"}, status=400)

        try:
            room = Room.objects.get(id=room_id)
            message = Message.objects.create(user=request.user, room=room, content=content)
            return JsonResponse({"message": message.content, "user": message.user.username})
        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)
