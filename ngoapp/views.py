from django.conf import settings
from django.shortcuts import render
from decimal import Decimal
from rest_framework.decorators import api_view,permission_classes
from django.core.mail import send_mail
from ngoapp.serializers import AboutUsItemSerializer, ActivitySerializer, AssociativeWingsSerializer, CarsouselItem1Serializer, ContactUsSerializer, DistrictAdminSerializer, DistrictMailSerializer, DonationSerializer, DonationSocietySerializer, FeedbackSerializer, LatestUpdateItemSerializer, MemberRegSerializer, RegionAdminSerializer
from django.db import IntegrityError
from .models import AboutUsItem, Activity, AllLog, AssociativeWings, CarsouselItem1, ContactUs, DistrictAdmin, DistrictMail, Donation, DonationSociety, Feedback, LatestUpdateItem, MemberReg, RegionAdmin
from .permissions import  IsAdminOrDistrictAdminSelf, IsAdminOrDistrictOrRegionAdmin, IsAdminOrRegionAdminSelf, IsAdminOrSelfUser, IsAdminRole, IsDistrictAdmin
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

            response_data = {
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "unique_id": user.unique_id,
                "role": user.role,
            }

           
            if user.role == "district-admin":
                try:
                    district_admin = DistrictAdmin.objects.get(
                        district_admin_id=user.unique_id
                    )
                    response_data["allocated_district"] = district_admin.allocated_district
                except DistrictAdmin.DoesNotExist:
                    response_data["allocated_district"] = None
            if user.role == "region-admin":
                try:
                    region_admin = RegionAdmin.objects.get(
                        region_admin_id=user.unique_id
                    )
                    response_data["allocated_district"] = region_admin.allocated_district
                except RegionAdmin.DoesNotExist:
                    response_data["allocated_district"] = None

            return Response(response_data, status=status.HTTP_200_OK)

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
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]  # unified class
        return [AllowAny()]

    def get(self, request):
        member_id = request.query_params.get("member_id")
        district = request.query_params.get("allocated_district")  # new param

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

        # Filter by district if provided
        queryset = MemberReg.objects.all().order_by("-created_at")
        if district:
            queryset = queryset.filter(district=district)  # assuming `district` is a field in MemberReg

        serializer = MemberRegSerializer(queryset, many=True)
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
        return [AllowAny()] if self.request.method == "GET" else [IsAdminOrDistrictAdminSelf()]

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
        serializer = ActivitySerializer(data=request.data,context={"request": request})
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

        serializer = ActivitySerializer(activity, data=request.data, partial=True,context={"request": request})
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
    
class DonationSocietyAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]   # anyone can donate
        return [IsAdminRole()]

    def get(self, request):
        donation_id = request.query_params.get("donation_id")

        if donation_id:
            donation = DonationSociety.objects.filter(
                donation_id=donation_id
            ).first()

            if not donation:
                return Response(
                    {"success": False, "message": "Donation not found"},
                    status=404
                )

            return Response(
                {"success": True, "data": DonationSocietySerializer(donation).data},
                status=200
            )

        donations = DonationSociety.objects.all().order_by("-created_at")

        return Response(
            {"success": True, "data": DonationSocietySerializer(donations, many=True).data},
            status=200
        )

    def post(self, request):
        serializer = DonationSocietySerializer(data=request.data)
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
class CarsouselItem1APIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

   
    def get(self, request):
       
        carousel_id = request.query_params.get("id")

        if carousel_id:
            carousel = CarsouselItem1.objects.filter(id=carousel_id).first()
            if not carousel:
                return Response({"success": False, "message": "Not found"}, status=404)

            return Response({"success": True, "data": CarsouselItem1Serializer(carousel).data})

        
        return Response({
            "success": True,
            "data": CarsouselItem1Serializer(
                CarsouselItem1.objects.all(),
                many=True
            ).data
        })

   
    def post(self, request):
        serializer = CarsouselItem1Serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,"message": "Carousel item created successfully"}, status=201)

        return Response({"success": False, "message": "Invalid data"}, status=400)

  
    def put(self, request):
        carousel_id = request.data.get("id")
        carousel = CarsouselItem1.objects.filter(id=carousel_id).first()

        if not carousel:
            return Response({"success": False, "message": "Carousel item not found"}, status=404)

        serializer = CarsouselItem1Serializer(carousel, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True,"message": "Carousel item updated successfully"})

        return Response({"success": False}, status=400)


    def delete(self, request):
        carousel_id = request.data.get("id")
        deleted, _ = CarsouselItem1.objects.filter(id=carousel_id).delete()

        if not deleted:
            return Response({"success": False, "message": "Carousel item not found"}, status=404)

        return Response({"success": True, "message": "Carousel item deleted successfully"})
class AboutUsItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]


    def get(self, request):
       
        about_id = request.query_params.get("id")

        if about_id:
            about = AboutUsItem.objects.filter(id=about_id).first()
            if not about:
                return Response(
                    {"success": False, "message": "AboutUs not found"},
                    status=404
                )

            return Response(
                {"success": True, "data": AboutUsItemSerializer(about).data}
            )

       

        about_list = AboutUsItem.objects.all().order_by("-created_at")
        return Response(
            {"success": True, "data": AboutUsItemSerializer(about_list, many=True).data}
        )

    def post(self, request):
        serializer = AboutUsItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "AboutUs created successfully"},
                status=201
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def put(self, request):
        about_id = request.data.get("id")
        if not about_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        about = AboutUsItem.objects.filter(id=about_id).first()
        if not about:
            return Response(
                {"success": False, "message": "AboutUs not found"},
                status=404
            )

        serializer = AboutUsItemSerializer(
            about, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "AboutUs updated successfully"}
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def delete(self, request):
        about_id = request.data.get("id")
        if not about_id:
            return Response(
                {"success": False, "message": "id is required"},
                status=400
            )

        deleted, _ = AboutUsItem.objects.filter(id=about_id).delete()
        if not deleted:
            return Response(
                {"success": False, "message": "AboutUs not found"},
                status=404
            )

        return Response(
            {"success": True, "message": "AboutUs deleted successfully"}
        )


class ContactUsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminRole()]
    
    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response(
                {"message": "Contact message submitted successfully!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        contacts = ContactUs.objects.all().order_by('-id')
        serializer = ContactUsSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DistrictAdminAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method in ("POST", "DELETE"):
            return [IsAdminRole()]

        if self.request.method in ("GET", "PUT"):
            return [IsAuthenticated(), IsAdminOrDistrictAdminSelf()]

        return [IsAuthenticated()]
    from django.db import IntegrityError

    def post(self, request):
        serializer = DistrictAdminSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"success": True, "message": "District admin created successfully"},
                    status=201
                )
            except IntegrityError as e:
                error_msg = str(e)

                if "email" in error_msg:
                    return Response(
                        {"success": False, "message": "Email already exists"},
                        status=400
                    )
                if "phone" in error_msg:
                    return Response(
                        {"success": False, "message": "Phone already exists"},
                        status=400
                    )

                return Response(
                    {"success": False, "message": "Duplicate entry"},
                    status=400
                )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def get(self, request):
        district_admin_id = request.query_params.get("district_admin_id")

        if district_admin_id:
            admin = DistrictAdmin.objects.filter(
                district_admin_id=district_admin_id
            ).first()

            if not admin:
                return Response(
                    {"success": False, "message": "District admin not found"},
                    status=404
                )

            serializer = DistrictAdminSerializer(admin)
            return Response(serializer.data)

        queryset = DistrictAdmin.objects.all().order_by("-id")
        serializer = DistrictAdminSerializer(queryset, many=True)
        return Response(serializer.data)
        
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

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"success": True, "message": "Member updated successfully"}
                )
        except IntegrityError as e:
            
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
           
            return Response(
                {"success": False, "message": "An error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class DistrictMailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsDistrictAdmin]

    def post(self, request):
       
        try:
            district_admin = DistrictAdmin.objects.get(
                district_admin_id=request.user.unique_id
            )
        except DistrictAdmin.DoesNotExist:
            return Response(
                {"success": False, "message": "District admin not found"},
                status=403
            )

        serializer = DistrictMailSerializer(data=request.data)

        if serializer.is_valid():
            try:
                member_ids = serializer.validated_data["member_ids"]

                members = MemberReg.objects.filter(
                    member_id__in=member_ids,
                    district=district_admin.allocated_district
                )

                if not members.exists():
                    return Response(
                        {"success": False, "message": "No valid members for your district"},
                        status=400
                    )
                emails = members.values_list("email", flat=True)
                send_mail(
                    subject=serializer.validated_data["subject"],
                    message=serializer.validated_data["message"],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(emails),
                    fail_silently=False,
                )
                DistrictMail.objects.create(
                    district_admin_id=district_admin,
                    subject=serializer.validated_data["subject"],
                    message=serializer.validated_data["message"],
                    member_ids=list(
                        members.values_list("member_id", flat=True)
                    )
                )

                return Response(
                    {"success": True, "message": "Mail sent successfully"},
                    status=201
                )

            except Exception as e:
                return Response(
                    {"success": False, "message": str(e)},
                    status=500
                )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )
@api_view(['GET'])
def associative_wing_name_list(request):
    names = AssociativeWings.objects.values_list('organization_name', flat=True)
    return Response(names)
class LatestUpdateItemAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAdminRole()]

    def get(self, request):
        item_id = request.query_params.get("id")

        if item_id:
            item = LatestUpdateItem.objects.filter(id=item_id).first()
            if not item:
                return Response(
                    {"success": False, "message": "Not found"},
                    status=404
                )

            serializer = LatestUpdateItemSerializer(item)
            return Response({
                "success": True,
                "data": serializer.data
            })

        latest_updates = LatestUpdateItem.objects.all().order_by("-created_at")
        serializer = LatestUpdateItemSerializer(latest_updates, many=True)

        return Response({
            "success": True,
            "data": serializer.data
        })

    def post(self, request):
        serializer = LatestUpdateItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Latest update created successfully"},
                status=201
            )

        return Response(
            {"success": False, "message": "Invalid data"},
            status=400
        )

    def put(self, request):
        item_id = request.data.get("id")
        item = LatestUpdateItem.objects.filter(id=item_id).first()

        if not item:
            return Response(
                {"success": False, "message": "Latest update not found"},
                status=404
            )

        serializer = LatestUpdateItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Latest update updated successfully"}
            )

        return Response({"success": False}, status=400)

    def delete(self, request):
        item_id = request.data.get("id")
        deleted, _ = LatestUpdateItem.objects.filter(id=item_id).delete()

        if not deleted:
            return Response(
                {"success": False, "message": "Latest update not found"},
                status=404
            )

        return Response(
            {"success": True, "message": "Latest update deleted successfully"}
        )
class RegionAdminAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method in ("POST", "DELETE"):
            return [IsAdminRole()]

        if self.request.method in ("GET", "PUT"):
            return [IsAuthenticated(), IsAdminOrRegionAdminSelf()]

        return [IsAuthenticated()]

    def post(self, request):
        serializer = RegionAdminSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"success": True, "message": "Region admin created successfully"},
                    status=201
                )
            except IntegrityError as e:
                error_msg = str(e)

                if "email" in error_msg:
                    return Response(
                        {"success": False, "message": "Email already exists"},
                        status=400
                    )
                if "phone" in error_msg:
                    return Response(
                        {"success": False, "message": "Phone already exists"},
                        status=400
                    )

                return Response(
                    {"success": False, "message": "Duplicate entry"},
                    status=400
                )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=400
        )

    def get(self, request):
        region_admin_id = request.query_params.get("region_admin_id")

        if region_admin_id:
            admin = RegionAdmin.objects.filter(
                region_admin_id=region_admin_id
            ).first()

            if not admin:
                return Response(
                    {"success": False, "message": "Region admin not found"},
                    status=404
                )

            serializer = RegionAdminSerializer(admin)
            return Response(serializer.data)

        queryset = RegionAdmin.objects.all().order_by("-id")
        serializer = RegionAdminSerializer(queryset, many=True)
        return Response(serializer.data)

    def put(self, request):
        region_admin_id = request.data.get("region_admin_id")

        if not region_admin_id:
            return Response(
                {"success": False, "message": "region_admin_id is required"},
                status=400
            )

        admin = RegionAdmin.objects.filter(
            region_admin_id=region_admin_id
        ).first()

        if not admin:
            return Response(
                {"success": False, "message": "Region admin not found"},
                status=404
            )

        serializer = RegionAdminSerializer(
            admin, data=request.data, partial=True
        )

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {"success": True, "message": "Region admin updated successfully"}
                )
        except IntegrityError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=400
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "An error occurred",
                    "details": str(e)
                },
                status=500
            )
class FeedbackAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        if self.request.method == "DELETE":
            return [IsAdminRole()]
        return [IsAdminRole()]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Feedback submitted successfully!"},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        feedbacks = Feedback.objects.all().order_by("-id")
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    def delete(self, request):
        feedback_id = request.data.get("id")

        if not feedback_id:
            return Response(
                {"success": False, "message": "Feedback id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted, _ = Feedback.objects.filter(id=feedback_id).delete()

        if not deleted:
            return Response(
                {"success": False, "message": "Feedback not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"success": True, "message": "Feedback deleted successfully"},
            status=status.HTTP_200_OK
        )
    def put(self, request):
        feedback_id = request.data.get("id")
        status_value = request.data.get("status")

        if not feedback_id:
            return Response(
                {"success": False, "message": "Feedback id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if status_value is None:
            return Response(
                {"success": False, "message": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated = Feedback.objects.filter(id=feedback_id).update(status=status_value)

        if not updated:
            return Response(
                {"success": False, "message": "Feedback not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"success": True, "message": "Feedback status updated successfully"},
            status=status.HTTP_200_OK
        )
@api_view(['GET'])
@permission_classes([IsAdminOrDistrictOrRegionAdmin])
def member_list_by_district(request):
    districts = request.query_params.getlist('district')

    if len(districts) == 1 and ',' in districts[0]:
        districts = districts[0].split(',')

    if not districts:
        return Response(
            {"error": "District parameter is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    members = MemberReg.objects.filter(district__in=districts)
    serializer = MemberRegSerializer(members, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)