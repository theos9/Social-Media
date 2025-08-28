from .models import User , Otp
from rest_framework import serializers , status
import random
from django.utils.timezone import now , timedelta

class OtpRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Otp
        fields = ['phone_number', 'purpose']

    def create(self, validated_data):
        phone = validated_data.pop('phone_number')

        code = str(random.randint(100000, 999999))
        expires_at = now() + timedelta(minutes=2)

        otp = Otp.objects.create(
            phone_number=phone,
            code=code,
            purpose=validated_data['purpose'],
            expires_at=expires_at
        )
        print(code)
        return otp

class UserRegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=6,write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'code']

    def validate(self, attrs):
        otp = Otp.objects.filter(
            phone_number=attrs['phone'],
            code=attrs['code'],
            is_used=False,
            expires_at__gt=now()
        ).first()
        if not otp:
            raise serializers.ValidationError("Invalid or expired OTP.",code=status.HTTP_400_BAD_REQUEST)
        return attrs
    
    def create(self, validated_data):
        Otp.objects.update(
            phone_number=validated_data['phone'],
            code=validated_data['code'],
            is_used=True,
            expires_at=now()
        )
        validated_data.pop('code')
        user = User.objects.create(**validated_data)
        return user