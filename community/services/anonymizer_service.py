import hashlib
import uuid
from django.conf import settings

def anonymize_user_data(username):
    """
    Anonymize a username while keeping it consistent for the same input
    Returns an anonymized version of the username
    """
    if not username:
        return "Anonymous"
    
    # Create a deterministic but anonymized username
    salt = getattr(settings, 'ANONYMIZER_SALT', 'default_salt_value')
    hash_input = f"{username}{salt}"
    hash_obj = hashlib.md5(hash_input.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Create a predictable anonymous name using the hash
    adjectives = ["Brave", "Calm", "Kind", "Wise", "Gentle", "Quiet", "Happy", "Friendly"]
    animals = ["Wolf", "Bear", "Eagle", "Deer", "Fox", "Owl", "Tiger", "Dolphin"]
    
    # Use the hash to deterministically select an adjective and animal
    adj_index = int(hash_hex[0:2], 16) % len(adjectives)
    animal_index = int(hash_hex[2:4], 16) % len(animals)
    
    # Construct anonymous name
    anonymous_name = f"{adjectives[adj_index]}{animals[animal_index]}"
    
    # Add a short unique identifier to avoid collisions
    short_id = hash_hex[-4:]
    
    return f"{anonymous_name}{short_id}"
