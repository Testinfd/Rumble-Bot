"""
Error handling and retry logic for Rumble Bot
"""
import time
import functools
from typing import Callable, Any, Optional, Dict
from enum import Enum

from .config import config
from .logger import log


class ErrorType(Enum):
    """Types of errors that can occur"""
    NETWORK_ERROR = "network_error"
    SELENIUM_ERROR = "selenium_error"
    FILE_ERROR = "file_error"
    TELEGRAM_ERROR = "telegram_error"
    RUMBLE_ERROR = "rumble_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class RetryableError(Exception):
    """Exception that indicates the operation should be retried"""
    def __init__(self, message: str, error_type: ErrorType = ErrorType.UNKNOWN_ERROR):
        super().__init__(message)
        self.error_type = error_type


class NonRetryableError(Exception):
    """Exception that indicates the operation should not be retried"""
    def __init__(self, message: str, error_type: ErrorType = ErrorType.UNKNOWN_ERROR):
        super().__init__(message)
        self.error_type = error_type


class ErrorHandler:
    """Handles errors and implements retry logic"""
    
    def __init__(self):
        """Initialize error handler"""
        self.error_counts = {}
        self.last_errors = {}
        
    def retry_on_failure(self, 
                        max_attempts: int = None,
                        delay: float = None,
                        backoff_factor: float = 2.0,
                        retryable_exceptions: tuple = None):
        """
        Decorator for retrying functions on failure
        
        Args:
            max_attempts: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            backoff_factor: Factor to multiply delay by after each failure
            retryable_exceptions: Tuple of exception types to retry on
        """
        if max_attempts is None:
            max_attempts = config.RETRY_ATTEMPTS
        
        if delay is None:
            delay = config.RETRY_DELAY_SECONDS
        
        if retryable_exceptions is None:
            retryable_exceptions = (RetryableError, ConnectionError, TimeoutError)
        
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        result = func(*args, **kwargs)
                        
                        # Reset error count on success
                        func_name = func.__name__
                        if func_name in self.error_counts:
                            self.error_counts[func_name] = 0
                        
                        return result
                        
                    except NonRetryableError as e:
                        log.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise
                    
                    except retryable_exceptions as e:
                        last_exception = e
                        attempt_num = attempt + 1
                        
                        # Track error
                        func_name = func.__name__
                        self.error_counts[func_name] = self.error_counts.get(func_name, 0) + 1
                        self.last_errors[func_name] = str(e)
                        
                        if attempt_num < max_attempts:
                            log.warning(f"Attempt {attempt_num}/{max_attempts} failed for {func.__name__}: {e}")
                            log.info(f"Retrying in {current_delay} seconds...")
                            time.sleep(current_delay)
                            current_delay *= backoff_factor
                        else:
                            log.error(f"All {max_attempts} attempts failed for {func.__name__}")
                    
                    except Exception as e:
                        # For unexpected exceptions, log and re-raise
                        log.error(f"Unexpected error in {func.__name__}: {e}")
                        raise NonRetryableError(f"Unexpected error: {e}")
                
                # If we get here, all retries failed
                raise last_exception
            
            return wrapper
        return decorator
    
    def handle_telegram_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle Telegram-related errors"""
        error_info = {
            'type': ErrorType.TELEGRAM_ERROR,
            'message': str(error),
            'context': context,
            'retryable': True
        }
        
        # Determine if error is retryable
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in ['rate limit', 'too many requests']):
            error_info['retryable'] = True
            error_info['suggested_delay'] = 60  # Wait longer for rate limits
        elif any(keyword in error_str for keyword in ['invalid token', 'unauthorized']):
            error_info['retryable'] = False
        elif any(keyword in error_str for keyword in ['network', 'connection', 'timeout']):
            error_info['retryable'] = True
        
        log.error(f"Telegram error ({context}): {error}")
        return error_info
    
    def handle_selenium_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle Selenium-related errors"""
        error_info = {
            'type': ErrorType.SELENIUM_ERROR,
            'message': str(error),
            'context': context,
            'retryable': True
        }
        
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in ['element not found', 'no such element']):
            error_info['retryable'] = True
        elif any(keyword in error_str for keyword in ['timeout', 'time out']):
            error_info['retryable'] = True
        elif any(keyword in error_str for keyword in ['session not created', 'driver']):
            error_info['retryable'] = False
        
        log.error(f"Selenium error ({context}): {error}")
        return error_info
    
    def handle_file_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle file-related errors"""
        error_info = {
            'type': ErrorType.FILE_ERROR,
            'message': str(error),
            'context': context,
            'retryable': False
        }
        
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in ['permission denied', 'access denied']):
            error_info['retryable'] = False
        elif any(keyword in error_str for keyword in ['no such file', 'file not found']):
            error_info['retryable'] = False
        elif any(keyword in error_str for keyword in ['disk full', 'no space']):
            error_info['retryable'] = False
        
        log.error(f"File error ({context}): {error}")
        return error_info
    
    def handle_rumble_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle Rumble-related errors"""
        error_info = {
            'type': ErrorType.RUMBLE_ERROR,
            'message': str(error),
            'context': context,
            'retryable': True
        }
        
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in ['login failed', 'invalid credentials']):
            error_info['retryable'] = False
        elif any(keyword in error_str for keyword in ['upload failed', 'processing error']):
            error_info['retryable'] = True
        elif any(keyword in error_str for keyword in ['rate limit', 'too many uploads']):
            error_info['retryable'] = True
            error_info['suggested_delay'] = 300  # Wait 5 minutes for upload limits
        
        log.error(f"Rumble error ({context}): {error}")
        return error_info
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors encountered"""
        return {
            'error_counts': self.error_counts.copy(),
            'last_errors': self.last_errors.copy(),
            'total_errors': sum(self.error_counts.values())
        }
    
    def reset_error_counts(self):
        """Reset error tracking"""
        self.error_counts.clear()
        self.last_errors.clear()
        log.info("Error counts reset")
    
    def is_healthy(self, max_errors_per_function: int = 10) -> bool:
        """Check if the system is healthy based on error counts"""
        for func_name, count in self.error_counts.items():
            if count > max_errors_per_function:
                log.warning(f"Function {func_name} has {count} errors (threshold: {max_errors_per_function})")
                return False
        return True


# Global error handler instance
error_handler = ErrorHandler()


def format_error_message(error: Exception, context: str = "") -> str:
    """Format error message for user display"""
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Create user-friendly error messages
    user_messages = {
        'ConnectionError': 'Network connection error. Please check your internet connection.',
        'TimeoutError': 'Operation timed out. Please try again.',
        'FileNotFoundError': 'File not found. Please check the file path.',
        'PermissionError': 'Permission denied. Please check file permissions.',
        'ValueError': 'Invalid input provided.',
        'RetryableError': 'Temporary error occurred. Retrying...',
        'NonRetryableError': 'Operation failed and cannot be retried.'
    }
    
    user_msg = user_messages.get(error_type, f"An error occurred: {error_msg}")
    
    if context:
        user_msg = f"{context}: {user_msg}"
    
    return user_msg


def log_system_info():
    """Log system information for debugging"""
    import platform
    import sys
    
    log.info(f"System: {platform.system()} {platform.release()}")
    log.info(f"Python: {sys.version}")
    log.info(f"Bot configuration: Max retries={config.RETRY_ATTEMPTS}, Delay={config.RETRY_DELAY_SECONDS}s")
