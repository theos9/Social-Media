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
            raise serializers.ValidationError({"detail":"Invalid or expired OTP."},code=status.HTTP_400_BAD_REQUEST)
        otp.is_used = True
        otp.expires_at = now()
        otp.save()
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('code')
        user = User.objects.create(**validated_data)
        return user
    
class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField(max_length=6, write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        otp = Otp.objects.filter(
            phone_number=phone,
            code=attrs['code'],
            is_used=False,
            expires_at__gt=now()
        ).first()
        try:
            user = User.objects.get(phone=phone, is_active=True)
            attrs['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail":"User not found or inactive."}, code=status.HTTP_404_NOT_FOUND)
        if not otp:
            raise serializers.ValidationError({"detail":"Invalid or expired OTP."},code=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.expires_at = now()
        otp.save()
        return attrs
    def create(self, validated_data):
        return validated_data['user']