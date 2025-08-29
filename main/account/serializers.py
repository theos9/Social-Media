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

class UserProfileSerializer(serializers.ModelSerializer):
    new_phone_number = serializers.CharField(write_only=True, required=False)
    otp_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    verify_phone = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['phone','is_phone_verified','first_name','last_name','username','avatar','bio','new_phone_number','otp_code','verify_phone']
        read_only_fields = ['phone','is_phone_verified']

    def validate(self, attrs):
        if attrs.get("username"):
            if User.objects.filter(username=attrs["username"]).exists():
                raise serializers.ValidationError({"detail": "Username already exists."}, code=status.HTTP_400_BAD_REQUEST)
        if attrs.get('verify_phone') and not attrs.get('otp_code'):
            raise serializers.ValidationError({"detail": "OTP code is required for phone verification."}, code=status.HTTP_400_BAD_REQUEST)
        if attrs.get('new_phone_number') and not attrs.get('otp_code'):
            raise serializers.ValidationError({"detail": "OTP code is required for phone number change."}, code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        new_phone = validated_data.pop('new_phone_number', None)
        otp_code = validated_data.pop('otp_code', None)
        verify_phone = validated_data.pop('verify_phone', False)

        if verify_phone and otp_code:
            otp_obj = Otp.objects.filter(
                phone_number=instance.phone,
                code=otp_code,
                is_used=False,
                expires_at__gt=now()
            ).first()

            if not otp_obj:
                raise serializers.ValidationError({"detail":"Invalid or expired OTP."},code=status.HTTP_400_BAD_REQUEST)

            otp_obj.is_used = True
            otp_obj.expires_at = now()
            otp_obj.save()
            instance.is_phone_verified = True

        if new_phone and otp_code:
            if not instance.is_phone_verified:
                raise serializers.ValidationError(
                    {"detail": "Phone number must be verified before changing it."},
                    code=status.HTTP_400_BAD_REQUEST
                )
            otp_obj = Otp.objects.filter(
                phone_number=new_phone,
                code=otp_code,
                is_used=False,
                expires_at__gt=now()
            ).first()
            if not otp_obj:
                raise serializers.ValidationError({"detail":"Invalid or expired OTP."},code=status.HTTP_400_BAD_REQUEST)
            otp_obj.is_used = True
            otp_obj.expires_at = now()
            otp_obj.save()
            instance.phone = new_phone

        return super().update(instance, validated_data)