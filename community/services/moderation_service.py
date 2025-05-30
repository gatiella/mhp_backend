
import re
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ContentModerationException(Exception):
    """Exception raised when content fails moderation checks"""
    pass

def check_content(content):
    """
    Check if content passes moderation rules
    Returns True if content is acceptable, False otherwise
    """
    if not content or not isinstance(content, str):
        return False
    
    # List of patterns to check
    patterns = [
        # Hate speech patterns
        r'\b(hate|kill|attack|destroy)\s+(group|community|people|race|gender)\b',
        # Explicit content patterns
        r'\b(explicit|pornographic|obscene)\b',
        # Personal information patterns
        r'\b(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})\b',  # Phone numbers
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # IP addresses
    ]
    
    # Check for any pattern matches
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            logger.warning(f"Content moderation failed: matched pattern '{pattern}'")
            return False
    
    # Optional integration with external API for more sophisticated checks
    if hasattr(settings, 'USE_EXTERNAL_MODERATION_API') and settings.USE_EXTERNAL_MODERATION_API:
        try:
            # This would be replaced with actual API call
            return _check_with_external_api(content)
        except Exception as e:
            logger.error(f"External moderation API error: {str(e)}")
            # Fall back to passed if external API fails
            return True
    
    return True

def _check_with_external_api(content):
    """
    Placeholder for external API integration
    Would call an external content moderation API
    """
    # Example implementation (not actually calling an API)
    # This would be replaced with actual API calls to services like:
    # - Google Cloud Content Moderation
    # - AWS Comprehend
    # - Azure Content Moderator
    return True  # Assume passes for now

