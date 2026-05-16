"""
Token encryption/decryption using Fernet symmetric encryption.
Tokens are encrypted before storage and decrypted only when needed for MCP connections.
"""

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

# Initialise Fernet with the secret key from settings
# The key must be a valid 32-byte URL-safe base64-encoded string
try:
    _fernet = Fernet(settings.SECRET_KEY.encode())
except Exception:
    # Provide a helpful error if the key is invalid
    raise ValueError(
        "SECRET_KEY is not a valid Fernet key. "
        # "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
    )


def encrypt_token(plaintext: str) -> str:
    """Encrypt a plaintext token and return a base64-encoded ciphertext string."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a ciphertext token back to plaintext. Raises ValueError on failure."""
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        raise ValueError("Failed to decrypt token — it may have been tampered with or the key has changed.")
