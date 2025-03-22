from django.urls import path
from . import views  # Import views from the same app
from .views import send_request, view_requests, accept_request, reject_request, view_connections
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home1/', views.home1, name='home1'),
    
    # Profile Management
    path('profile/add-education/', views.add_education, name='add_education'),
    path('profile/add-experience/', views.add_experience, name='add_experience'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('edit-bio/', views.edit_bio, name='edit_bio'), 
   
    path('connections/', views.view_connections, name='view_connections'),
    path('send_request/<int:receiver_id>/', views.send_request, name='send_request'),
    path('view_requests/', views.view_requests, name='view_requests'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('view_connections/<int:user_id>/', views.view_connections, name='view_connections'),
    path('connections/requests/', views.connection_requests, name='connection_requests'),
    path('connections/accept/<int:connection_id>/', views.accept_connection, name='accept_connection'),
    path('connections/reject/<int:connectio_id>/', views.reject_connection, name='reject_connection'),
    path('connections/my/', views.my_connections, name='my_connections'),
    path('connections/send/<str:username>/', views.send_connection_request, name='send_connection_request')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)