from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import OtpRequestSerializer , UserRegisterSerializer , UserLoginSerializer
from .models import Otp
from rest_framework_simplejwt.tokens import RefreshToken

class OtpRequestView(generics.CreateAPIView):
    queryset = Otp.objects.all()
    serializer_class = OtpRequestSerializer

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        },status=status.HTTP_200_OK)