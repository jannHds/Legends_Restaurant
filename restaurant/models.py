from django.db import models
'''models.py

Database tables 

User

MenuItem

Category

Order

Cart

Staff handling

Manager tools '''
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("staff", "Staff"),
        ("manager", "Manager"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    def is_customer(self):
        return self.role == "customer"

    def is_staff_user(self):
        return self.role == "staff"

    def is_manager(self):
        return self.role == "manager"
