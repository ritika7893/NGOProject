from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import MemberReg, AllLog
 # adjust import path if needed


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
