from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add other profile details if needed

class Transaction(models.Model):
    CALL_TYPE_CHOICES = [
        ('short', 'Short'),
        ('long', 'Long'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES, blank=True, null=True)
    shares = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)

    # Add fields for transactions (e.g., symbol, amount, date)
    def __str__(self):
        return f"{self.symbol} - {self.amount}"



