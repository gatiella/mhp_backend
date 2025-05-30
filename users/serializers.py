from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
import uuid

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_picture',
                  'date_of_birth', 'bio', 'mental_health_goals', 'stress_level',
                  'preferred_activities', 'is_email_verified', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_email_verified', 'created_at', 'updated_at')

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # Deactivate until email verification
        user.email_verification_token = uuid.uuid4()
        user.save()
        
        # Send verification email
        self.send_verification_email(user)
        
        return user
    
    def send_verification_email(self, user):
        verification_url = f"{settings.FRONTEND_URL}/api/users/verify-email/{user.email_verification_token}/"
        
        subject = "Verify Your Email - Mental Health Partner"
        message = f"""
        Hi {user.username},
        
        Thank you for registering with Mental Health Partner!
        
        Please click the link below to verify your email address:
        {verification_url}
        
        If you didn't create this account, please ignore this email.
        
        Best regards,
        Mental Health Partner Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        return attrs

class TokenSerializer(serializers.Serializer):
    """
    Serializer for JWT tokens.
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    
    @classmethod
    def get_token(cls, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }
class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password request.
    """
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs        