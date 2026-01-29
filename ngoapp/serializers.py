from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import AboutUsItem, Activity, AssociativeWings, CarsouselItem1, ContactUs, DistrictAdmin, Donation, DonationSociety, MemberReg, AllLog
 # adjust import path if needed
from django.utils import timezone

class MemberRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberReg
        fields = "__all__"
        extra_kwargs = {
            "email": {"validators": []},
            "phone": {"validators": []},
        }

    def create(self, validated_data):
        raw_password = validated_data.pop("password", None)

        if raw_password:
            validated_data["password"] = make_password(raw_password)

        member = MemberReg.objects.create(**validated_data)

        # create AllLog entry
        AllLog.objects.create(
            unique_id=member.member_id,
            email=member.email,
            phone=member.phone,
            password=member.password,
            role="member",
            is_verified=True
        )

        return member

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if password:
            hashed_password = make_password(password)
            instance.password = hashed_password

            AllLog.objects.filter(
                unique_id=instance.member_id
            ).update(password=hashed_password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
class AssociativeWingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssociativeWings
        fields = "__all__"
        read_only_fields = ["id","created_at","updated_at"]

class ActivitySerializer(serializers.ModelSerializer):
    is_past = serializers.SerializerMethodField()
    is_present = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = "__all__"
        read_only_fields = ["activity_id", "is_past", "is_present", "is_upcoming",]
    def calculate_amounts(self, activity_fee):
        portal_charges = activity_fee * Decimal("0.05")
        transaction_charges = activity_fee * Decimal("0.02")
        tax_amount = (activity_fee + portal_charges + transaction_charges) * Decimal("0.18")
        total_amount = activity_fee + portal_charges + transaction_charges + tax_amount

        return {
            "portal_charges": portal_charges,
            "transaction_charges": transaction_charges,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
        }

    def create(self, validated_data):
        activity_fee = validated_data.get("activity_fee", Decimal("0.00"))
        validated_data.update(self.calculate_amounts(activity_fee))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        activity_fee = validated_data.get(
            "activity_fee", instance.activity_fee
        )
        validated_data.update(self.calculate_amounts(activity_fee))
        return super().update(instance, validated_data)
    def get_is_past(self, obj):
        if not obj.activity_date_time:
            return False
        return obj.activity_date_time.date() < timezone.now().date()

    def get_is_present(self, obj):
        if not obj.activity_date_time:
            return False
        return obj.activity_date_time.date() == timezone.now().date()

    def get_is_upcoming(self, obj):
        if not obj.activity_date_time:
            return False
        return obj.activity_date_time.date() > timezone.now().date()
    
class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = "__all__"
        read_only_fields = [  "donation_id","status", "payment_reference", "created_at"]


class DonationSocietySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationSociety
        fields = "__all__"
        read_only_fields = [  "donation_id","status", "payment_reference", "created_at"]

class CarsouselItem1Serializer(serializers.ModelSerializer):
    class Meta:
        model = CarsouselItem1
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class AboutUsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsItem
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = "__all__"

class DistrictAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictAdmin
        fields = "__all__"
        extra_kwargs = {
            "email": {"validators": []},
            "phone": {"validators": []},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        raw_password = validated_data.pop("password", None)

        if raw_password:
            validated_data["password"] = make_password(raw_password)

        district_admin = DistrictAdmin.objects.create(**validated_data)

        # Create AllLog entry
        AllLog.objects.create(
            unique_id=district_admin.district_admin_id,  # or custom id if you have one
            email=district_admin.email,
            phone=district_admin.phone,
            password=district_admin.password,
            role="district-admin",
            is_verified=True
        )

        return district_admin

    def update(self, instance, validated_data):
        # Track changes for DistrictAdmin
        changes = {}

        # Handle password separately
        password = validated_data.pop("password", None)
        if password:
            hashed_password = make_password(password)
            if instance.password != hashed_password:
                instance.password = hashed_password
                changes["password"] = hashed_password

        # Update other fields in DistrictAdmin
        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)
                changes[attr] = value

        instance.save()

        # Only update fields that exist in AllLog
        alllog_fields = {f.name for f in AllLog._meta.get_fields()}
        filtered_changes = {k: v for k, v in changes.items() if k in alllog_fields}

        if filtered_changes:
            AllLog.objects.filter(unique_id=instance.district_admin_id).update(**filtered_changes)

        return instance
