from datetime import datetime, timedelta, UTC
import hashlib
import os
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pwdlib import PasswordHash

from config import settings

# Initialize password hashing using modern recommended libraries
password_hash_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


# ---------------- CRYPTOGRAPHIC CORE UTILITIES ---------------- #

def hash_password(password: str) -> str:
    """
    Hashes a raw password string using the recommended Argon2/Bcrypt profile.
    """
    return password_hash_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its storage hash.
    """
    return password_hash_context.verify(plain_password, hashed_password)


def creat_acces_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Generates an encrypted JWT access token for user authentication sessions.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key.get_secret_value(), 
        algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_acces_token(token: str) -> str | None:
    """
    Decodes a JWT token and verifies its expiration, returning the user's email if valid.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key.get_secret_value(), 
            algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


def generate_reset_token() -> str:
    """
    Generates a secure, random URL-safe token for password reset sequences.
    """
    return os.urandom(32).hex()


def hash_reset_token(token: str) -> str:
    """
    Computes a SHA-256 hash of a reset token to securely store it in the database.
    """
    return hashlib.sha256(token.encode()).hexdigest()