from django.urls import path
from .views import users_directory
from .import views
urlpatterns = [
    path('directory/', users_directory, name='users_directory'),
    path('send_connection_request/<int:user_id>/', views.send_connection_request, name='send_connection_request'),
]