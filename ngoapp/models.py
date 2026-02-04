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
    gender = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    primary_membership=models.CharField(max_length=100, blank=True, null=True)
    district=models.CharField(max_length=200, blank=True, null=True)
    state=models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.member_id:
            self.member_id = generate_id("MEM")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.member_id})"

class AssociativeWings(models.Model):
    organization_name = models.CharField(max_length=255)
    native_wing = models.CharField(max_length=255,blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_person_name = models.CharField(max_length=255,blank=True, null=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    image = models.ImageField(upload_to='associative_wings/', blank=True, null=True)
   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name

class Activity(models.Model):
    activity_name = models.CharField(max_length=255)
    activity_id = models.CharField( max_length=30,unique=True,editable=False)
    objective = models.TextField(blank=True, null=True)
    activity_date_time = models.DateTimeField(blank=True, null=True)
    district=models.CharField(max_length=100,blank=True, null=True)
    venue = models.CharField(max_length=255,blank=True, null=True)
    image = models.ImageField(upload_to='activities/', blank=True, null=True)
    activity_fee = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    portal_charges = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    transaction_charges = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    created_by = models.CharField(max_length=30, blank=True, null=True)
    updated_by = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.activity_id:
            while True:
                activity_id = generate_id("ACT")
                if not Activity.objects.filter(activity_id=activity_id).exists():
                    self.activity_id = activity_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.activity_name} ({self.activity_id})"
class Donation(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )
    donation_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )
    activity_id = models.CharField(max_length=30)  # no FK (safe for payments)
    full_name = models.CharField(max_length=255, blank=True,null=True)
    email = models.EmailField( blank=True,null=True)
    phone = models.CharField(max_length=15, blank=True,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
  
    status = models.CharField( max_length=10,choices=STATUS_CHOICES,default="pending")
    payment_reference = models.CharField(max_length=100, blank=True,null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.donation_id:
            while True:
                donation_id = generate_id("DON")
                if not Donation.objects.filter(donation_id=donation_id).exists():
                    self.donation_id = donation_id
                    break
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.full_name} - {self.amount} ({self.status})"

class DonationSociety(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )
    donation_id = models.CharField( max_length=30,unique=True,
        editable=False
    )
    purpose = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, blank=True,null=True)
    email = models.EmailField( blank=True,null=True)
    phone = models.CharField(max_length=15, blank=True,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField( max_length=10,choices=STATUS_CHOICES,default="pending")
    payment_reference = models.CharField(max_length=100, blank=True,null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.donation_id:
            while True:
                donation_id = generate_id("DON")
                if not Donation.objects.filter(donation_id=donation_id).exists():
                    self.donation_id = donation_id
                    break
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.full_name} - {self.amount} ({self.status})"
    

class CarsouselItem1(models.Model):
    title=models.CharField(max_length=200)
    sub_title=models.CharField(max_length=200,blank=True,null=True)
    description=models.TextField(blank=True,null=True)
    image=models.ImageField(upload_to="carousel_images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AboutUsItem(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True,null=True)  
    image=models.ImageField(upload_to="aboutus_images/")
    module=models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ContactUs(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15,blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.full_name} - {self.subject}"
    
class DistrictAdmin(models.Model):
    district_admin_id=models.CharField(max_length=20,unique=True,editable=False)    
    full_name=models.CharField(max_length=200,blank=True, null=True)
    email=models.EmailField(unique=True,blank=True, null=True)
    phone=models.CharField(max_length=15, unique=True,blank=True, null=True)
    password=models.CharField(max_length=255,blank=True, null=True)
    allocated_district=models.CharField(max_length=100,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.district_admin_id:
            while True:
                district_admin_id = generate_id("DIST/ADM")
                if not DistrictAdmin.objects.filter(
                    district_admin_id=district_admin_id
                ).exists():
                    self.district_admin_id = district_admin_id
                    break
        super().save(*args, **kwargs)

class DistrictMail(models.Model):
    district_admin_id = models.ForeignKey(DistrictAdmin,on_delete=models.CASCADE,related_name="sent_mails",to_field='district_admin_id')
    member_ids = models.JSONField(default=list, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.sender.district_admin_id}"
    
class LatestUpdateItem(models.Model):
    title=models.CharField(max_length=200)
    link=models.CharField(max_length=300,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RegionAdmin(models.Model):
    region_admin_id=models.CharField(max_length=20,unique=True,editable=False)    
    full_name=models.CharField(max_length=200,blank=True, null=True)
    email=models.EmailField(unique=True,blank=True, null=True)
    phone=models.CharField(max_length=15, unique=True,blank=True, null=True)
    password=models.CharField(max_length=255,blank=True, null=True)
    allocated_district=models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        if not self.region_admin_id:
            while True:
                region_admin_id = generate_id("REG/ADM")
                if not RegionAdmin.objects.filter(
                    region_admin_id=region_admin_id
                ).exists():
                    self.region_admin_id = region_admin_id
                    break
        super().save(*args, **kwargs)

class Feedback(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15,blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class AdminMail(models.Model):
    admin_id = models.ForeignKey(AllLog,on_delete=models.CASCADE,related_name="sent_mails",to_field='unique_id')
    member_ids = models.JSONField(default=list, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.admin_id}"