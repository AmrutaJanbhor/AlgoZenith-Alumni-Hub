from django.urls import path
from events import views
from .views import create_event, event_list,event_detail,register_for_event
urlpatterns = [
    path('create/', create_event, name='create_event'),
    path('list/', event_list, name='event_list'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('event/<int:event_id>/register/', register_for_event, name='register_for_event'),
    
]