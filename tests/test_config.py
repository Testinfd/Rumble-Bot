"""
Tests for configuration module
"""
import pytest
import os
from unittest.mock import patch
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config import Config


class TestConfig:
    """Test configuration management"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = Config()
        
        assert config.MAX_FILE_SIZE_MB == 2048
        assert config.UPLOAD_TIMEOUT_SECONDS == 1800
        assert config.RETRY_ATTEMPTS == 3
        assert config.HEADLESS_MODE == True
        assert config.LOG_LEVEL == "INFO"
    
    @patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token_123',
        'RUMBLE_EMAIL': 'test@example.com',
        'RUMBLE_PASSWORD': 'test_password',
        'MAX_FILE_SIZE_MB': '1024',
        'HEADLESS_MODE': 'false'
    })
    def test_environment_override(self):
        """Test that environment variables override defaults"""
        config = Config()
        
        assert config.TELEGRAM_BOT_TOKEN == 'test_token_123'
        assert config.RUMBLE_EMAIL == 'test@example.com'
        assert config.RUMBLE_PASSWORD == 'test_password'
        assert config.MAX_FILE_SIZE_MB == 1024
        assert config.HEADLESS_MODE == False
    
    @patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': 'test_token',
        'RUMBLE_EMAIL': 'test@example.com',
        'RUMBLE_PASSWORD': 'test_password'
    })
    def test_validation_success(self):
        """Test successful validation"""
        config = Config()
        assert config.validate() == True
    
    @patch.dict(os.environ, {
        'TELEGRAM_BOT_TOKEN': '',
        'RUMBLE_EMAIL': 'test@example.com',
        'RUMBLE_PASSWORD': 'test_password'
    })
    def test_validation_failure(self):
        """Test validation failure with missing token"""
        config = Config()
        
        with pytest.raises(ValueError) as exc_info:
            config.validate()
        
        assert "TELEGRAM_BOT_TOKEN" in str(exc_info.value)
    
    def test_boolean_conversion(self):
        """Test boolean environment variable conversion"""
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('', True),  # Default for HEADLESS_MODE
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'HEADLESS_MODE': env_value}):
                config = Config()
                assert config.HEADLESS_MODE == expected
