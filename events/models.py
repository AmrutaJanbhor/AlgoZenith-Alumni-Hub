from django.db import models
from django.conf import settings

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Links to User model
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, choices=[
        ('Workshop', 'Workshop'),
        ('Seminar', 'Seminar'),
        ('Meetup', 'Meetup'),
        ('Fundraising', 'Fundraising'),
    ], default='Meetup')


    def _str_(self):
        return self.title


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')  # Prevent duplicate registrations

    def _str_(self):
        return f"{self.user.username} registered for {self.event.title}"
    
class Donation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="donations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} donated {self.amount} to {self.event.title}"

class DonationTransaction(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name="transactions")
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')

    def _str_(self):
        return f"Transaction {self.transaction_id} - {self.status}"
