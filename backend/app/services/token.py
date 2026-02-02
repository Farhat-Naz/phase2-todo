"""
Token service for generating and verifying secure tokens.

Provides:
- generate_secure_token(): Generate cryptographically secure random tokens
- hash_token(): Hash tokens with bcrypt for secure storage
- verify_token_hash(): Verify plain token against hashed token

Used for:
- Password reset tokens (US2)
- Email verification tokens (US3)
- Any other security-sensitive token operations

Security:
- Uses secrets.token_urlsafe() for CSPRNG (Cryptographically Secure Pseudo-Random Number Generator)
- Tokens are hashed with bcrypt before database storage
- Tokens are never logged or exposed in error messages
"""
import secrets
import bcrypt
from typing import Optional


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Uses Python's secrets module which provides CSPRNG suitable for
    security-sensitive applications like password reset and email verification.

    Args:
        length: Token length in bytes (default: 32 bytes = 43 chars URL-safe base64)

    Returns:
        str: URL-safe random token string

    Security:
        - Uses secrets.token_urlsafe() which is CSPRNG
        - Default 32 bytes provides 256 bits of entropy
        - URL-safe encoding (base64 with - and _ instead of + and /)
        - Suitable for password reset and email verification

    Example:
        token = generate_secure_token()  # Returns something like: "abc123def456..."
        short_token = generate_secure_token(length=16)  # Shorter token
    """
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """
    Hash a token using bcrypt for secure storage.

    Tokens should NEVER be stored in plain text in the database.
    Always hash tokens before storing and compare hashed values.

    Args:
        token: Plain text token to hash

    Returns:
        str: Bcrypt-hashed token string

    Security:
        - Uses bcrypt with automatic salt generation
        - Bcrypt is intentionally slow to resist brute-force attacks
        - Hash output includes algorithm, cost, salt, and hash
        - Safe to store in database

    Example:
        plain_token = generate_secure_token()
        hashed = hash_token(plain_token)
        # Store hashed in database, send plain_token to user via email
    """
    # Encode token to bytes
    token_bytes = token.encode('utf-8')

    # Generate salt and hash token
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(token_bytes, salt)

    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_token_hash(plain_token: str, hashed_token: str) -> bool:
    """
    Verify a plain token against its hashed version.

    Used to validate tokens from user requests (email links, API calls)
    against hashed tokens stored in database.

    Args:
        plain_token: Plain text token from user (e.g., from URL parameter)
        hashed_token: Hashed token from database

    Returns:
        bool: True if token matches hash, False otherwise

    Security:
        - Constant-time comparison to prevent timing attacks
        - Never logs or exposes token values
        - Returns False for any error (invalid hash format, etc.)

    Example:
        # User clicks link with token in URL
        token_from_url = request.query_params.get("token")

        # Fetch hashed token from database
        db_token = db.query(PasswordResetToken).filter(...).first()

        # Verify token
        if verify_token_hash(token_from_url, db_token.token_hash):
            # Token is valid, proceed with password reset
            pass
        else:
            # Token is invalid or expired
            raise HTTPException(status_code=400, detail="Invalid token")
    """
    try:
        # Encode both token and hash to bytes
        token_bytes = plain_token.encode('utf-8')
        hashed_bytes = hashed_token.encode('utf-8')

        # Use bcrypt's checkpw for constant-time comparison
        return bcrypt.checkpw(token_bytes, hashed_bytes)

    except Exception:
        # Any error (invalid hash format, encoding issues, etc.) = invalid token
        # Do NOT log exception details (may contain sensitive token data)
        return False


# Example usage and testing
if __name__ == "__main__":
    # Generate a new token
    token = generate_secure_token()
    print(f"Generated token: {token}")
    print(f"Token length: {len(token)} characters")

    # Hash the token
    hashed = hash_token(token)
    print(f"\nHashed token: {hashed}")
    print(f"Hash length: {len(hashed)} characters")

    # Verify the token
    is_valid = verify_token_hash(token, hashed)
    print(f"\nToken verification: {is_valid}")  # Should be True

    # Try with wrong token
    wrong_token = generate_secure_token()
    is_valid = verify_token_hash(wrong_token, hashed)
    print(f"Wrong token verification: {is_valid}")  # Should be False
