from django.db import models

# Create your models here.
from datetime import datetime
from django.utils import timezone
import random
from django.db import models


# Create your models here.
def generate_id(prefix):
    current_year = datetime.now().year
    random_number = random.randint(100000, 999999)
    return f"{prefix}/{current_year}/{random_number}"

class AllLog(models.Model):
    id = models.AutoField(primary_key=True)
    unique_id = models.CharField(unique=True, max_length=50, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=255,default='')
    role = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

class MemberReg(models.Model):
    member_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True,null=True)
    address = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    occupation = models.CharField(max_length=150, blank=True, null=True)
    designation = models.CharField(max_length=150, blank=True, null=True)
    department_name = models.CharField(max_length=150, blank=True, null=True)
    organization_name = models.CharField(max_length=200, blank=True, null=True)
    nature_of_work = models.TextField(blank=True, null=True)
    education_level = models.CharField(max_length=150, blank=True, null=True)
    other_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.member_id:
            self.member_id = generate_id("MEM")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.member_id})"