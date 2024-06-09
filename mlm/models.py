from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import uuid
from decimal import Decimal

PREMIUM_AMOUNT = Decimal('40.00')
COMMISSION_RATE_LEVEL_1 = Decimal('0.10')

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    referral_code = models.CharField(max_length=255)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals_made')
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Add this line
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Add this line
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def generate_referral_code(self):
        self.referral_code = uuid.uuid4().hex[:10].upper()
        self.save()

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = get_random_string(10)
        super().save(*args, **kwargs)

    def calculate_and_save_commission(self, level):
        commission_rate = {
            1: 0.10,
            2: 0.15,
            3: 0.20,
            4: 0.25,
            5: 0.30
        }
        commission_amount = PREMIUM_AMOUNT * commission_rate[level]
        Commission.objects.create(user=self, amount=commission_amount, level=level)

    def __str__(self):
        return self.username

class Referral(models.Model):
    referrer = models.ForeignKey(User, related_name='referrer_set', on_delete=models.CASCADE)
    referred = models.ForeignKey(User, related_name='referred_set', on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.referrer.calculate_and_save_commission(self.level)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred.username} at level {self.level}"

class Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    level = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ZAR - Level {self.level} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"



class RecentActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity}"

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"
    
class ReferredUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_user_set')
    level = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} referred {self.referred_user.username} at level {self.level}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.user.username

