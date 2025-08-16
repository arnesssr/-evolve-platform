"""Utility functions for reseller app"""
import random
import string
import hashlib
import time


def generate_partner_code(user_id=None, prefix="EVOLVE"):
    """
    Generate a unique partner code for resellers.
    
    Args:
        user_id: The user ID to include in the code (optional)
        prefix: The prefix for the partner code (default: EVOLVE)
    
    Returns:
        str: A formatted partner code like EVOLVE-A1B2C3D4
    """
    # Create a unique identifier using multiple factors
    if user_id:
        # Combine user_id with timestamp for uniqueness
        unique_string = f"{user_id}-{time.time()}-{random.randint(1000, 9999)}"
        # Create a hash of the unique string
        hash_object = hashlib.sha256(unique_string.encode())
        hex_dig = hash_object.hexdigest()
        
        # Take first 8 characters of the hash and convert to uppercase alphanumeric
        # Mix letters and numbers for better readability
        code_chars = []
        for i, char in enumerate(hex_dig[:8]):
            if i % 2 == 0 and char.isdigit():
                # Keep digits as is
                code_chars.append(char)
            else:
                # Convert to uppercase letter
                if char.isdigit():
                    # Convert digit to letter (0-9 to A-J)
                    code_chars.append(chr(ord('A') + int(char)))
                else:
                    code_chars.append(char.upper())
        
        unique_code = ''.join(code_chars[:8])
    else:
        # Generate completely random code
        # Mix of uppercase letters and digits, formatted as XXXX-XXXX
        part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        unique_code = f"{part1}{part2}"
    
    return f"{prefix}-{unique_code}"


def format_partner_code(code):
    """
    Ensure partner code follows the correct format.
    
    Args:
        code: The partner code to format
    
    Returns:
        str: Formatted partner code
    """
    if not code:
        return None
    
    # If code doesn't start with EVOLVE, prepend it
    if not code.startswith("EVOLVE-"):
        # Remove any existing prefix like REF- or RSL-
        if "-" in code:
            _, suffix = code.split("-", 1)
            return f"EVOLVE-{suffix}"
        else:
            return f"EVOLVE-{code}"
    
    return code
