from django.urls import path,include

from .views import AboutUsItemAPIView, ActivityAPIView, AssociativeWingsAPIView, CarsouselItem1APIView, ContactUsAPIView, DistrictAdminAPIView, DistrictMailAPIView, DonationAPIView, DonationSocietyAPIView, LoginAPIView, MemberRegAPIView, RefreshTokenAPIView, associative_wing_name_list
urlpatterns = [
    path('login/',LoginAPIView.as_view(),name='login'),
    path('refresh-token/', RefreshTokenAPIView.as_view(),name="refresh-token"),
    path('member-reg/', MemberRegAPIView.as_view(), name="member-list-create"),
    path('associative-wings/', AssociativeWingsAPIView.as_view(), name="associative-wings"),
    path('activity-items/',ActivityAPIView.as_view(),name='activity-items'),
    path('donate/',DonationAPIView.as_view(),name='donate'),
    path('donate-society/',DonationSocietyAPIView.as_view(),name='donate-society'),
    path('carousel1-item/', CarsouselItem1APIView.as_view(), name="carousel-api"),
    path('aboutus-item/',AboutUsItemAPIView.as_view(),name="aboutus-api"),
    path('contact-us/',ContactUsAPIView.as_view(),name='contact-us'),
    path('district-reg/',DistrictAdminAPIView.as_view(),name='district-admin'),
    path('district-mail/',DistrictMailAPIView.as_view(),name='district-mail'),
    path('associative-wing-names/',associative_wing_name_list,name='associative-wing-names'),
]