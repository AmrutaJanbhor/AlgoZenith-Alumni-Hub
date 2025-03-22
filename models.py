from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('alumni', 'Alumni'),
    ]
    is_approved = models.BooleanField(default=False)  # Admin approval field
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_alumni = models.BooleanField(default=False)
    AUTH_USER_MODEL = "users.User"
    
    def _str_(self):
        return self.username

class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="education")
    degree = models.CharField(max_length=100)
    institution = models.CharField(max_length=200)
    year_of_passing = models.IntegerField()

    def _str_(self):
        return f"{self.degree} - {self.institution}"

class WorkExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="work_experience")
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField(blank=True, null=True)  # Null for current job

    def _str_(self):
        return f"{self.position} at {self.company}"
    
class Alumni(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Corrected
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)

    def _str_(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.user.username}'s Profile"  

class ConnectionRequest(models.Model):
    sender = models.ForeignKey(User, related_name='connection_requests_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='connection_requests_received', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"


class Connection(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='connections_initiated',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='connections_received',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def _str_(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"