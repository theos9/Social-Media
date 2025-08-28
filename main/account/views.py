from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import OtpRequestSerializer , UserRegisterSerializer
from .models import Otp

class OtpRequestView(generics.CreateAPIView):
    queryset = Otp.objects.all()
    serializer_class = OtpRequestSerializer

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
