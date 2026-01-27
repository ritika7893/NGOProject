from django.urls import path,include

from .views import LoginAPIView, MemberRegAPIView
urlpatterns = [
    path('login/',LoginAPIView.as_view(),name='login'),
      path("member-reg/", MemberRegAPIView.as_view(), name="member-list-create"),
]