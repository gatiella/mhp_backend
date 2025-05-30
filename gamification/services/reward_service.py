import random
import string
import hashlib
from datetime import datetime

def generate_redemption_code(reward, user):
    """
    Generate a unique redemption code for a reward
    Uses a template if available, otherwise creates a random code
    """
    if reward.code_template:
        # Use the template and replace placeholders
        code = reward.code_template
        replacements = {
            '{USERNAME}': user.username,
            '{USERID}': str(user.id),
            '{DATE}': datetime.now().strftime('%Y%m%d'),
            '{RANDOM4}': ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
            '{RANDOM6}': ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
            '{RANDOM8}': ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
        }
        
        for placeholder, value in replacements.items():
            code = code.replace(placeholder, value)
            
        return code
    else:
        # Generate a random code
        # Create a unique basis using reward ID, user ID and timestamp
        unique_basis = f"{reward.id}-{user.id}-{datetime.now().timestamp()}"
        
        # Create a hash and use it as basis for the code
        hash_obj = hashlib.md5(unique_basis.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Format into a readable code (e.g., ABC12-DEF34-GHI56)
        code_parts = [
            hash_hex[0:5].upper(),
            hash_hex[5:10].upper(),
            hash_hex[10:15].upper()
        ]
        return '-'.join(code_parts)
