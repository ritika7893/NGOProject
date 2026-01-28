from django.urls import path,include

from .views import ActivityAPIView, AssociativeWingsAPIView, DonationAPIView, LoginAPIView, MemberRegAPIView, RefreshTokenAPIView
urlpatterns = [
    path('login/',LoginAPIView.as_view(),name='login'),
    path("refresh-token/", RefreshTokenAPIView.as_view(),name="refresh-token"),
    path("member-reg/", MemberRegAPIView.as_view(), name="member-list-create"),
    path("associative-wings/", AssociativeWingsAPIView.as_view(), name="associative-wings"),
    path('activity-items/',ActivityAPIView.as_view(),name='activity-items'),
    path('donate/',DonationAPIView.as_view(),name='donate'),
]