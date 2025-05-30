# conversation/views.py
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    MessageCreateSerializer
)
from .services.deepseek_service import DeepseekService
from .services.safety_checker import SafetyChecker
from api.permissions import IsOwner

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    """
    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def message(self, request, pk=None):
        """
        Send a message in a conversation and get AI response.
        """
        try:
            conversation = self.get_object()
            
            # Validate and create user message
            serializer = MessageCreateSerializer(
                data={'content': request.data.get('content', ''), 'sender': 'user'},
                context={'conversation_id': conversation.pk}
            )
            serializer.is_valid(raise_exception=True)
            user_message = serializer.save()
            
            # Initialize services
            safety_checker = SafetyChecker()
            deepseek_service = DeepseekService()
            
            # Safety check
            is_safe, intervention_message = safety_checker.check_message(user_message.content)
            
            if not is_safe:
                ai_message = Message.objects.create(
                    conversation=conversation,
                    content=intervention_message,
                    sender='ai'
                )
            else:
                # Get conversation history
                conversation_history = list(conversation.messages.all().order_by('created_at'))
                
                # Generate AI response with error handling
                try:
                        ai_response = deepseek_service.generate_response(
                            user_message.content, 
                            conversation_history
                        ) or "I'm having trouble generating a response."  # Ensures non-None

                        is_response_safe, safe_response = safety_checker.check_response(
                            ai_response, 
                            user_message.content
                        )

                        ai_message = Message.objects.create(
                            conversation=conversation,
                            content=safe_response,
                            sender='ai'
                        )
                except Exception as ai_error:
                        print(f"AI Response Error: {str(ai_error)}")
                        ai_message = Message.objects.create(
                            conversation=conversation,
                            content="I'm having trouble generating a response. Please try again.",
                            sender='ai'
                        )

            
            conversation.save()
            
            return Response({
                'user_message': MessageSerializer(user_message).data,
                'ai_message': MessageSerializer(ai_message).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error in message endpoint: {str(e)}")
            return Response(
                {'error': 'An error occurred while processing your message'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )