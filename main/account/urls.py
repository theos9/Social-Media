from django.urls import path
from .views import OtpRequestView, UserRegisterView

urlpatterns = [
    path('otp/request/', OtpRequestView.as_view(), name='otp-request'),
    path('user/register/', UserRegisterView.as_view(), name='user-register'),
]
