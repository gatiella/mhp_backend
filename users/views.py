import uuid
from django.conf import settings
from django.views import View
from rest_framework import status, generics, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer, TokenSerializer
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.save()
            return Response({
                'message': 'Account created successfully. Please check your email to verify your account.',
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    API view for user login.
    """
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if not user.is_email_verified:
                return Response({
                    'error': 'Please verify your email before logging in.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            token = TokenSerializer.get_token(user)
            return Response(token, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class VerifyEmailView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, token):
        try:
            user = get_object_or_404(User, email_verification_token=token)
            if user.is_email_verified:
                return render(request, 'email_verification.html', {
                    'success': True,
                    'message': 'Your email was already verified.'
                })
            
            user.is_email_verified = True
            user.is_active = True
            user.save()
            
            return render(request, 'email_verification.html', {
                'success': True,
                'message': 'Email verified successfully. You can now log in.'
            })
            
        except User.DoesNotExist:
            return render(request, 'email_verification.html', {
                'success': False,
                'message': 'Invalid verification token.'
            })

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile retrieval and update.
    """
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        # Handle file upload separately
        profile_picture = self.request.FILES.get('profile_picture')
        if profile_picture:
            self.request.user.profile_picture = profile_picture
        serializer.save()
        
class ForgotPasswordView(APIView):
    """
    API view for password reset request.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            user.password_reset_token = uuid.uuid4()
            user.save()
            
            # Send reset email
            self.send_reset_email(user)
            
            return Response({
                'message': 'Password reset link sent to your email'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response({
                'message': 'Password reset link sent to your email'
            }, status=status.HTTP_200_OK)
    
    def send_reset_email(self, user):
        # Use regular HTTP URL that's clickable in emails
        #reset_url = f"{settings.FRONTEND_URL}/api/users/reset-redirect/{user.password_reset_token}/"
        reset_url = f"{settings.FRONTEND_URL}/api/users/web-reset/{user.password_reset_token}/"
        
        subject = "Reset Your Password - Mental Health Partner"
        message = f"""
        Hi {user.username},
        
        You requested to reset your password for Mental Health Partner.
        
        Please click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this, please ignore this email.
        
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

class ResetPasswordRedirectView(APIView):
    """
    Web page that redirects to Flutter app or web version
    """
    permission_classes = (AllowAny,)
    
    def get(self, request, token):
        try:
            # Verify token exists
            user = User.objects.get(password_reset_token=token)
            return render(request, 'auth/web_reset_form.html', {
                'token': token,
                'valid': True
            })
        except User.DoesNotExist:
            return render(request, 'auth/web_reset_form.html', {
                'token': token,
                'valid': False
            })

class ResetPasswordView(APIView):
    """
    API view for password reset confirmation.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request, token):
        new_password = request.data.get('password')
        if not new_password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(password_reset_token=token)
            user.set_password(new_password)
            user.password_reset_token = None  # Clear the token
            user.save()
            
            return Response({
                'message': 'Password reset successfully'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'Invalid reset token'}, status=status.HTTP_400_BAD_REQUEST)

class WebResetPasswordFormView(View):
    def get(self, request, token):
        try:
            user = User.objects.get(password_reset_token=token)
            return render(request, 'auth/web_reset_form.html', {
                'token': token,
                'valid': True
            })
        except User.DoesNotExist:
            return render(request, 'auth/web_reset_form.html', {
                'token': token,
                'valid': False,
                'error': 'Invalid or expired reset token'
            })

    def post(self, request, token):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or not confirm_password:
            return render(request, 'auth/web_reset_form.html', {
                'token': token,
                'valid': True,
                'error': 'Both password fields are required'
            })

        if password != confirm_password:
            return render(request, 'auth/web_reset_form.html', {
                'token': token,
                'valid': True,
                'error': 'Passwords do not match'
            })

        try:
            user = User.objects.get(password_reset_token=token)
            user.set_password(password)
            user.password_reset_token = None
            user.save()
            # Render success page with deep link
            return render(request, 'auth/web_reset_success.html')
        except User.DoesNotExist:
            return render(request, 'auth/web_reset_form.html', {
                'token': token,
                'valid': False,
                'error': 'Invalid or expired reset token'
            })