from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import AboutUsItem, Activity, AssociativeWings, CarsouselItem1, ContactUs, Donation, DonationSociety, MemberReg, AllLog
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