from django.shortcuts import render

from ngoapp.serializers import ActivitySerializer, AssociativeWingsSerializer, DonationSerializer, MemberRegSerializer

from .models import Activity, AllLog, AssociativeWings, Donation, MemberReg
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

class RefreshTokenAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            return Response(
                {
                    "access": str(access)
                },
                status=status.HTTP_200_OK
            )

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
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

class AssociativeWingsAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        wing_id = request.query_params.get("id")

        if wing_id:
            try:
                wing = AssociativeWings.objects.get(id=wing_id)
                serializer = AssociativeWingsSerializer(wing)
                return Response({"success": True, "data": serializer.data})
            except AssociativeWings.DoesNotExist:
                return Response(
                    {"success": False, "message": "Associative wing not found"},
                    status=404
                )

        wings = AssociativeWings.objects.all().order_by("-id")
        serializer = AssociativeWingsSerializer(wings, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = AssociativeWingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Associative wing created successfully"
                },
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        wing_id = request.data.get("id")
        if not wing_id:
            return Response(
                {"success": False, "message": "ID is required"},
                status=400
            )

        try:
            wing = AssociativeWings.objects.get(id=wing_id)
        except AssociativeWings.DoesNotExist:
            return Response(
                {"success": False, "message": "Associative wing not found"},
                status=404
            )

        serializer = AssociativeWingsSerializer(
            wing, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Associative wing updated successfully"
                }
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        wing_id = request.data.get("id")
        if not wing_id:
            return Response(
                {"success": False, "message": "ID is required"},
                status=400
            )

        try:
            AssociativeWings.objects.get(id=wing_id).delete()
            return Response(
                {
                    "success": True,
                    "message": "Associative wing deleted successfully"
                }
            )
        except AssociativeWings.DoesNotExist:
            return Response(
                {"success": False, "message": "Associative wing not found"},
                status=404
            )
class ActivityAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        activity_id = request.query_params.get("activity_id")

        if activity_id:
            activity = Activity.objects.filter(activity_id=activity_id).first()
            if not activity:
                return Response(
                    {"success": False, "message": "Activity not found"},
                    status=404
                )

            return Response(
                {"success": True, "data": ActivitySerializer(activity).data}
            )

        activities = Activity.objects.all().order_by("-id")
        return Response(
            {"success": True, "data": ActivitySerializer(activities, many=True).data}
        )

    def post(self, request):
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Activity created successfully"},
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        activity_id = request.data.get("activity_id")
        if not activity_id:
            return Response(
                {"success": False, "message": "activity_id is required"},
                status=400
            )

        activity = Activity.objects.filter(activity_id=activity_id).first()
        if not activity:
            return Response(
                {"success": False, "message": "Activity not found"},
                status=404
            )

        serializer = ActivitySerializer(activity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Activity updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        activity_id = request.data.get("activity_id")
        if not activity_id:
            return Response(
                {"success": False, "message": "activity_id is required"},
                status=400
            )

        deleted, _ = Activity.objects.filter(activity_id=activity_id).delete()
        if not deleted:
            return Response(
                {"success": False, "message": "Activity not found"},
                status=404
            )

        return Response(
            {"success": True, "message": "Activity deleted successfully"}
        )
class DonationAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]          # anyone can donate
        return [IsAdminRole()]  
    
    def get(self, request):
        donation_id = request.query_params.get("donation_id")
        activity_id = request.query_params.get("activity_id")

       
        if donation_id:
            donation = Donation.objects.filter(donation_id=donation_id).first()
            if not donation:
                return Response(
                    {"success": False, "message": "Donation not found"},
                    status=404
                )

            return Response(
                {"success": True, "data": DonationSerializer(donation).data}
            )

      
        donations = Donation.objects.all()

        if activity_id:
            donations = donations.filter(activity_id=activity_id)

        donations = donations.order_by("-created_at")

        return Response(
            {"success": True, "data": DonationSerializer(donations, many=True).data}
        )

    def post(self, request):
        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(status="PENDING")
            return Response(
                {"success": True, "message": "Donation created successfully"},
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )