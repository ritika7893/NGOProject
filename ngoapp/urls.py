from django.urls import path,include

from .views import LoginAPIView, MemberRegAPIView, RefreshTokenAPIView
urlpatterns = [
    path('login/',LoginAPIView.as_view(),name='login'),
    path("refresh-token/", RefreshTokenAPIView.as_view(),name="refresh-token"),
    path("member-reg/", MemberRegAPIView.as_view(), name="member-list-create"),
]