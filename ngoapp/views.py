from django.shortcuts import render

from ngoapp.serializers import MemberRegSerializer

from .models import AllLog, MemberReg
from .permissions import IsAdminRole
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password,check_password

# Create your views here.
class LoginAPIView(APIView):
    def post(self, request):
        email_or_phone = request.data.get("email_or_phone")
        password = request.data.get("password")

        if not email_or_phone or not password:
            return Response(
                {"error": "Email/Phone and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get user
            if "@" in email_or_phone:
                user = AllLog.objects.get(email=email_or_phone)
            else:
                user = AllLog.objects.get(phone=email_or_phone)

            if not user.is_active or not user.is_verified:
                return Response(
                    {"error": "Account is disabled"},
                    status=status.HTTP_403_FORBIDDEN
                )
          

            if not check_password(password, user.password):
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            
            refresh = RefreshToken.for_user(user)
            refresh["unique_id"] = user.unique_id
            refresh["role"] = user.role

            return Response(
                {
                    "message": "Login successful",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "unique_id": user.unique_id,
                    "role": user.role,
                },
                status=status.HTTP_200_OK
            )

        except AllLog.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class MemberRegAPIView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        member_id = request.query_params.get("member_id")

        if member_id:
            try:
                member = MemberReg.objects.get(member_id=member_id)
                serializer = MemberRegSerializer(member)
                return Response({"success": True, "data": serializer.data})
            except MemberReg.DoesNotExist:
                return Response(
                    {"success": False, "message": "Member not found"},
                    status=404
                )

        members = MemberReg.objects.all().order_by("-created_at")
        serializer = MemberRegSerializer(members, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = MemberRegSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.save()

        return Response({
            "success": True,
            "message": "Member registered successfully",
            "member_id": member.member_id
        }, status=status.HTTP_201_CREATED)

    def put(self, request):
        member_id = request.data.get("member_id")

        if not member_id:
            return Response(
                {"success": False, "message": "member_id is required"},
                status=400
            )

        try:
            member = MemberReg.objects.get(member_id=member_id)
        except MemberReg.DoesNotExist:
            return Response(
                {"success": False, "message": "Member not found"},
                status=404
            )

        serializer = MemberRegSerializer(
            member, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Member updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )
