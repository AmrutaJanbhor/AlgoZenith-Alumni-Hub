from django.urls import path
from . import views
from .views import chat_room,chat_list

urlpatterns = [
    path('',chat_list,name='chat_list'),
    path('chat/<int:user_id>/', chat_room, name='chat_room'),
    path('chat/send/<int:room_id>/', views.send_message, name='send_message'),
]