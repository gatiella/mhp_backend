import os
import json
import logging
import requests
from decouple import config
from django.conf import settings

logger = logging.getLogger(__name__)

class DeepseekService:
    """Official service for Deepseek via OpenRouter"""
    
    def __init__(self):
        # TEMPORARY DEBUG - Direct assignment of API key
        self.api_key = config('DEEPSEEK_API_KEY', default='')        # Once working, you can switch back to:
        # self.api_key = config('DEEPSEEK_API_KEY', default='')
            
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat-v3-0324:free"
        self.site_url = config('SITE_URL', default='http://localhost:8000')
        
    def generate_response(self, user_message, conversation_history=None):
        """Generate actual API response from Deepseek with improved error handling"""
        if not self.api_key:
            logger.error("Deepseek API credentials not configured")
            raise ValueError("Deepseek API credentials not configured")
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.site_url,
                "X-Title": "Mental Health Partner",
                "Content-Type": "application/json"
            }
            
            # Build message history with system prompt
            messages = [{
                "role": "system",
                "content": self._get_system_prompt()
            }]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg.sender == "user" else "assistant"
                    messages.append({"role": role, "content": msg.content})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Prepare API payload - limit to last 3 exchanges (6 messages) to avoid context length issues
            payload = {
                "model": self.model,
                "messages": messages[-6:],  # Keep last 3 exchanges
                "temperature": 0.7,
                "max_tokens": 350,
                "top_p": 0.9
            }
            
            logger.debug(f"Sending request to Deepseek API with {len(messages)} messages")
            
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            # Handle rate limiting specifically (before calling raise_for_status)
            if response.status_code == 429:
                rate_limit_message = "I'm currently unavailable due to high demand. Please try again later."
                logger.warning(f"OpenRouter rate limit exceeded: {response.text}")
                return rate_limit_message
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            # Parse response data
            result = response.json()
            logger.debug(f"Received response from Deepseek API: {result}")
            
            # Check if response contains the expected structure
            if "choices" not in result:
                logger.error(f"API response missing 'choices' key: {result}")
                return "I'm having trouble processing your request. Please try again."
                
            if not result["choices"] or "message" not in result["choices"][0]:
                logger.error(f"API response has invalid structure: {result}")
                return "I received an incomplete response. Please try again."
                
            # Extract and return the message content
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else 'unknown'
            error_text = e.response.text[:200] if hasattr(e, 'response') else str(e)
            error_detail = f"HTTP {status_code}: {error_text}"
            logger.error(f"Deepseek API HTTP error: {error_detail}")
            raise Exception(f"API request failed: {error_detail}")
            
        except requests.exceptions.Timeout:
            logger.error("Deepseek API request timed out")
            raise Exception("API request timed out")
            
        except requests.exceptions.ConnectionError:
            logger.error("Connection error when calling Deepseek API")
            raise Exception("Connection to API failed")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in API response: {str(e)}")
            raise Exception("Invalid API response format")
            
        except Exception as e:
            logger.error(f"Unexpected error in Deepseek service: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")
    
    def _get_system_prompt(self):
        """Safety-focused mental health prompt"""
        return """You are an empathetic mental health supporter. Follow these rules:
1. Use active listening and validation
2. Ask open-ended questions
3. Suggest coping strategies
4. Never diagnose conditions
5. Recommend professional help if needed
6. Responses must be concise (2-3 sentences)
7. Use simple, clear language
8. If crisis detected, provide emergency contacts"""