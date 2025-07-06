"""
Security service for SQL injection prevention and input sanitization.
"""
import re
import html
import json
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class SecurityService:
    """
    Comprehensive security service for preventing SQL injection and sanitizing inputs.
    """
    
    # Common SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\s|^)(union|select|insert|update|delete|drop|create|alter|exec|execute|sp_|xp_)(\s|$)",
        r"(\s|^)(or|and)(\s)+[\d\w]*(\s)*(=|like|in|not in)(\s)*[\d\w]*(\s)*(--|#|\/\*)",
        r"(--|#|\/\*|\*\/)",
        r"(\s|^)(char|ascii|substring|right|left|reverse|concat|concat_ws)(\s)*\(",
        r"(\s|^)(benchmark|sleep|waitfor|delay|pg_sleep)(\s)*\(",
        r"(\s|^)(information_schema|sys\.|mysql\.|pg_|sqlite_master)",
        r"(\\x[0-9a-f]{2})",
        r"(\s|^)(load_file|into outfile|into dumpfile)(\s)",
        r"(\s|^)(union(\s)+all(\s)+select)",
        r"(0x[0-9a-f]+)"
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<form[^>]*>.*?</form>",
        r"<input[^>]*>",
        r"vbscript:",
        r"data:text/html"
    ]
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 255, allow_html: bool = False) -> str:
        """
        Sanitize string input to prevent SQL injection and XSS.
        
        Args:
            input_str: The input string to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags (will escape them if False)
            
        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return str(input_str)
        
        # Limit length
        sanitized = input_str[:max_length]
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Check for SQL injection patterns
        for pattern in SecurityService.SQL_INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Potential SQL injection attempt detected: {sanitized}")
                # Remove the malicious pattern
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Check for XSS patterns
        if not allow_html:
            for pattern in SecurityService.XSS_PATTERNS:
                if re.search(pattern, sanitized, re.IGNORECASE):
                    logger.warning(f"Potential XSS attempt detected: {sanitized}")
                    # Remove the malicious pattern
                    sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
            # Escape HTML entities
            sanitized = html.escape(sanitized)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], allowed_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Sanitize dictionary input recursively.
        
        Args:
            data: Dictionary to sanitize
            allowed_keys: List of allowed keys (if provided, only these keys will be kept)
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return {}
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            clean_key = SecurityService.sanitize_string(str(key), max_length=100)
            
            # Check if key is allowed
            if allowed_keys and clean_key not in allowed_keys:
                logger.warning(f"Unauthorized key detected: {key}")
                continue
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = SecurityService.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = SecurityService.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[clean_key] = SecurityService.sanitize_list(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[clean_key] = value
            else:
                # Convert other types to string and sanitize
                sanitized[clean_key] = SecurityService.sanitize_string(str(value))
        
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """
        Sanitize list input recursively.
        
        Args:
            data: List to sanitize
            
        Returns:
            Sanitized list
        """
        if not isinstance(data, list):
            return []
        
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized.append(SecurityService.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(SecurityService.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(SecurityService.sanitize_list(item))
            elif isinstance(item, (int, float, bool)):
                sanitized.append(item)
            else:
                sanitized.append(SecurityService.sanitize_string(str(item)))
        
        return sanitized
    
    @staticmethod
    def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize user input for authentication and user management.
        
        Args:
            data: User input data
            
        Returns:
            Sanitized user data
        """
        allowed_keys = [
            'username', 'email', 'password', 'full_name', 'phone', 
            'company', 'location', 'bio', 'role'
        ]
        
        # Basic sanitization
        sanitized = SecurityService.sanitize_dict(data, allowed_keys)
        
        # Additional validation for specific fields
        if 'username' in sanitized:
            # Username should only contain alphanumeric characters and underscores
            username = sanitized['username']
            if not re.match(r'^[a-zA-Z0-9_]{3,50}$', username):
                raise ValueError("Username must be 3-50 characters and contain only letters, numbers, and underscores")
            sanitized['username'] = username.lower()
        
        if 'email' in sanitized:
            # Basic email validation
            email = sanitized['email']
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValueError("Invalid email format")
            sanitized['email'] = email.lower()
        
        if 'phone' in sanitized and sanitized['phone']:
            # Phone number should only contain digits, spaces, +, -, (, )
            phone = sanitized['phone']
            if not re.match(r'^[\d\s\+\-\(\)]{10,20}$', phone):
                raise ValueError("Invalid phone number format")
        
        return sanitized
    
    @staticmethod
    def validate_device_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize device input data.
        
        Args:
            data: Device input data
            
        Returns:
            Sanitized device data
        """
        allowed_keys = [
            'device_id', 'name', 'location', 'status', 'device_type',
            'relay1', 'relay2', 'relay3', 'relay4'
        ]
        
        # Basic sanitization
        sanitized = SecurityService.sanitize_dict(data, allowed_keys)
        
        # Additional validation for specific fields
        if 'device_id' in sanitized:
            device_id = sanitized['device_id']
            if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', device_id):
                raise ValueError("Device ID must be 1-50 characters and contain only letters, numbers, hyphens, and underscores")
        
        if 'status' in sanitized:
            status = sanitized['status'].lower()
            if status not in ['online', 'offline', 'maintenance']:
                raise ValueError("Status must be 'online', 'offline', or 'maintenance'")
            sanitized['status'] = status
        
        # Validate relay states
        for relay_key in ['relay1', 'relay2', 'relay3', 'relay4']:
            if relay_key in sanitized:
                relay_value = sanitized[relay_key].lower()
                if relay_value not in ['on', 'off']:
                    raise ValueError(f"{relay_key} must be 'on' or 'off'")
                sanitized[relay_key] = relay_value
        
        return sanitized
    
    @staticmethod
    def safe_query_execution(db: Session, query_func, *args, **kwargs):
        """
        Safely execute a database query with error handling.
        
        Args:
            db: Database session
            query_func: Function that performs the query
            *args: Arguments for the query function
            **kwargs: Keyword arguments for the query function
            
        Returns:
            Query result or None if error occurred
        """
        try:
            return query_func(db, *args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database query error: {str(e)}")
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {str(e)}")
            db.rollback()
            raise
    
    @staticmethod
    def sanitize_search_query(query: str, max_length: int = 100) -> str:
        """
        Sanitize search query input.
        
        Args:
            query: Search query string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized search query
        """
        if not isinstance(query, str):
            return ""
        
        # Limit length
        sanitized = query[:max_length]
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>&"\'%;(){}[\]\\]', '', sanitized)
        
        # Remove excessive whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized.strip()


class SecureQueryBuilder:
    """
    Builder class for creating secure database queries.
    """
    
    @staticmethod
    def build_user_search_query(db: Session, search_term: str, limit: int = 50):
        """
        Build a secure user search query.
        
        Args:
            db: Database session
            search_term: Search term (will be sanitized)
            limit: Maximum number of results
            
        Returns:
            Query result
        """
        # Sanitize search term
        safe_term = SecurityService.sanitize_search_query(search_term)
        
        if not safe_term:
            return []
        
        # Use parameterized query with SQLAlchemy ORM
        from models.user import User
        return db.query(User).filter(
            User.username.ilike(f'%{safe_term}%') |
            User.full_name.ilike(f'%{safe_term}%') |
            User.email.ilike(f'%{safe_term}%')
        ).limit(limit).all()
    
    @staticmethod
    def build_device_search_query(db: Session, search_term: str, limit: int = 50):
        """
        Build a secure device search query.
        
        Args:
            db: Database session
            search_term: Search term (will be sanitized)
            limit: Maximum number of results
            
        Returns:
            Query result
        """
        # Sanitize search term
        safe_term = SecurityService.sanitize_search_query(search_term)
        
        if not safe_term:
            return []
        
        # Use parameterized query with SQLAlchemy ORM
        from models.database import Device
        return db.query(Device).filter(
            Device.name.ilike(f'%{safe_term}%') |
            Device.location.ilike(f'%{safe_term}%') |
            Device.device_id.ilike(f'%{safe_term}%')
        ).limit(limit).all()


# Decorator for automatic input sanitization
def sanitize_inputs(validation_func=None):
    """
    Decorator to automatically sanitize function inputs.
    
    Args:
        validation_func: Optional function to validate specific input types
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Sanitize keyword arguments
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    sanitized_kwargs[key] = SecurityService.sanitize_string(value)
                elif isinstance(value, dict):
                    sanitized_kwargs[key] = SecurityService.sanitize_dict(value)
                elif isinstance(value, list):
                    sanitized_kwargs[key] = SecurityService.sanitize_list(value)
                else:
                    sanitized_kwargs[key] = value
            
            # Apply additional validation if provided
            if validation_func:
                sanitized_kwargs = validation_func(sanitized_kwargs)
            
            return func(*args, **sanitized_kwargs)
        return wrapper
    return decorator
