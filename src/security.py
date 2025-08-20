"""
Security utilities for Rumble Bot
"""
import os
import base64
import hashlib
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .config import config
from .logger import log


class CredentialManager:
    """Manages secure storage and retrieval of credentials"""
    
    def __init__(self):
        """Initialize credential manager"""
        self._encryption_key = None
        self._salt = b'rumble_bot_salt_2024'  # In production, use random salt
        
    def _get_encryption_key(self, password: str = None) -> bytes:
        """Get or generate encryption key"""
        if self._encryption_key:
            return self._encryption_key
        
        if not password:
            # Use a default password based on system info (not secure for production)
            password = f"rumble_bot_{os.getenv('COMPUTERNAME', 'default')}"
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self._salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self._encryption_key = key
        return key
    
    def encrypt_credential(self, credential: str, password: str = None) -> str:
        """Encrypt a credential string"""
        try:
            key = self._get_encryption_key(password)
            f = Fernet(key)
            encrypted = f.encrypt(credential.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            log.error(f"Error encrypting credential: {e}")
            return credential  # Return original if encryption fails
    
    def decrypt_credential(self, encrypted_credential: str, password: str = None) -> str:
        """Decrypt a credential string"""
        try:
            key = self._get_encryption_key(password)
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_credential.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            log.error(f"Error decrypting credential: {e}")
            return encrypted_credential  # Return original if decryption fails
    
    def mask_credential(self, credential: str, show_chars: int = 4) -> str:
        """Mask credential for logging purposes"""
        if not credential or len(credential) <= show_chars:
            return "*" * len(credential) if credential else ""
        
        return credential[:show_chars] + "*" * (len(credential) - show_chars)
    
    def validate_credentials(self) -> Dict[str, bool]:
        """Validate that all required credentials are present"""
        validation_results = {}
        
        # Check Telegram bot token
        telegram_token = config.TELEGRAM_BOT_TOKEN
        validation_results['telegram_token'] = bool(telegram_token and len(telegram_token) > 20)
        
        # Check Rumble credentials
        rumble_email = config.RUMBLE_EMAIL
        rumble_password = config.RUMBLE_PASSWORD
        validation_results['rumble_email'] = bool(rumble_email and '@' in rumble_email)
        validation_results['rumble_password'] = bool(rumble_password and len(rumble_password) >= 6)
        
        return validation_results
    
    def get_masked_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary with masked sensitive data"""
        return {
            'telegram_token': self.mask_credential(config.TELEGRAM_BOT_TOKEN),
            'rumble_email': self.mask_credential(config.RUMBLE_EMAIL, show_chars=3),
            'rumble_password': self.mask_credential(config.RUMBLE_PASSWORD, show_chars=0),
            'max_file_size_mb': config.MAX_FILE_SIZE_MB,
            'headless_mode': config.HEADLESS_MODE,
            'retry_attempts': config.RETRY_ATTEMPTS,
            'log_level': config.LOG_LEVEL
        }


class SecurityValidator:
    """Validates security aspects of the bot"""
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate that file path is safe"""
        try:
            # Normalize path
            normalized_path = os.path.normpath(file_path)
            
            # Check for path traversal attempts
            if '..' in normalized_path:
                log.warning(f"Path traversal attempt detected: {file_path}")
                return False
            
            # Check if path is within allowed directories
            allowed_dirs = [
                config.DOWNLOADS_DIR,
                config.TEMP_DIR,
                os.path.abspath('.')
            ]
            
            abs_path = os.path.abspath(normalized_path)
            for allowed_dir in allowed_dirs:
                if abs_path.startswith(os.path.abspath(allowed_dir)):
                    return True
            
            log.warning(f"File path outside allowed directories: {file_path}")
            return False
            
        except Exception as e:
            log.error(f"Error validating file path: {e}")
            return False
    
    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size is within limits"""
        max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            log.warning(f"File size {file_size} exceeds limit {max_size_bytes}")
            return False
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent security issues"""
        import re
        
        # Remove or replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255-len(ext)] + ext
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "file"
        
        return sanitized
    
    @staticmethod
    def validate_telegram_user(user_id: int, allowed_users: list = None) -> bool:
        """Validate if Telegram user is allowed to use the bot"""
        if not allowed_users:
            return True  # Allow all users if no restriction
        
        return user_id in allowed_users
    
    @staticmethod
    def check_rate_limit(user_id: int, max_requests: int = 10, window_minutes: int = 60) -> bool:
        """Check if user is within rate limits"""
        # This is a simple in-memory rate limiter
        # In production, use Redis or database
        import time
        
        if not hasattr(SecurityValidator, '_rate_limits'):
            SecurityValidator._rate_limits = {}
        
        current_time = time.time()
        window_start = current_time - (window_minutes * 60)
        
        # Clean old entries
        if user_id in SecurityValidator._rate_limits:
            SecurityValidator._rate_limits[user_id] = [
                timestamp for timestamp in SecurityValidator._rate_limits[user_id]
                if timestamp > window_start
            ]
        else:
            SecurityValidator._rate_limits[user_id] = []
        
        # Check if user is within limits
        if len(SecurityValidator._rate_limits[user_id]) >= max_requests:
            log.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Add current request
        SecurityValidator._rate_limits[user_id].append(current_time)
        return True


class ConfigValidator:
    """Validates configuration settings"""
    
    @staticmethod
    def validate_all() -> Dict[str, Any]:
        """Validate all configuration settings"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate required settings
        required_settings = {
            'TELEGRAM_BOT_TOKEN': config.TELEGRAM_BOT_TOKEN,
            'RUMBLE_EMAIL': config.RUMBLE_EMAIL,
            'RUMBLE_PASSWORD': config.RUMBLE_PASSWORD
        }
        
        for setting_name, setting_value in required_settings.items():
            if not setting_value:
                results['errors'].append(f"Missing required setting: {setting_name}")
                results['valid'] = False
        
        # Validate numeric settings
        numeric_settings = {
            'MAX_FILE_SIZE_MB': config.MAX_FILE_SIZE_MB,
            'UPLOAD_TIMEOUT_SECONDS': config.UPLOAD_TIMEOUT_SECONDS,
            'RETRY_ATTEMPTS': config.RETRY_ATTEMPTS,
            'SELENIUM_TIMEOUT': config.SELENIUM_TIMEOUT
        }
        
        for setting_name, setting_value in numeric_settings.items():
            if not isinstance(setting_value, (int, float)) or setting_value <= 0:
                results['errors'].append(f"Invalid numeric setting: {setting_name} = {setting_value}")
                results['valid'] = False
        
        # Validate file size limits
        if config.MAX_FILE_SIZE_MB > 2048:
            results['warnings'].append("MAX_FILE_SIZE_MB is very large, may cause issues")
        
        # Validate timeout settings
        if config.UPLOAD_TIMEOUT_SECONDS < 300:
            results['warnings'].append("UPLOAD_TIMEOUT_SECONDS is quite low for large files")
        
        return results


# Global instances
credential_manager = CredentialManager()
security_validator = SecurityValidator()
config_validator = ConfigValidator()
