from django.urls import path
from .views import OtpRequestView, UserRegisterView, UserLoginView, UserProfileView

urlpatterns = [
    path('otp/request/', OtpRequestView.as_view(), name='otp-request'),
    path('user/register/', UserRegisterView.as_view(), name='user-register'),
    path('user/login/', UserLoginView.as_view(), name='user-login'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),

]
