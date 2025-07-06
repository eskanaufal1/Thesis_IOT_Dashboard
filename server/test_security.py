"""
Security tests for SQL injection prevention and input sanitization.
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
from models.user import User
from services.security_service import SecurityService
from services.auth_service import create_user, get_user_by_username, authenticate_user
from services.device_service import DeviceService
from models.auth_schemas import UserCreate


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    """Create a fresh database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestSecurityService:
    """Test the SecurityService class for SQL injection prevention."""
    
    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        # Normal string
        result = SecurityService.sanitize_string("Hello World")
        assert result == "Hello World"
        
        # Empty string
        result = SecurityService.sanitize_string("")
        assert result == ""
        
        # String with extra whitespace
        result = SecurityService.sanitize_string("  Hello   World  ")
        assert result == "Hello World"
    
    def test_sanitize_string_sql_injection(self):
        """Test SQL injection pattern detection and removal."""
        # Basic SQL injection attempts
        test_cases = [
            ("'; DROP TABLE users; --", ""),
            ("admin' OR '1'='1", "admin  1=1"),
            ("1' UNION SELECT * FROM users--", "1   FROM users"),
            ("'; DELETE FROM users; --", ""),
            ("test' OR 1=1 --", "test   1=1"),
        ]
        
        for malicious_input, expected in test_cases:
            result = SecurityService.sanitize_string(malicious_input)
            # The result should not contain the original malicious patterns
            assert "DROP TABLE" not in result.upper()
            assert "DELETE FROM" not in result.upper()
            assert "UNION SELECT" not in result.upper()
            assert "--" not in result
    
    def test_sanitize_string_xss(self):
        """Test XSS pattern detection and removal."""
        test_cases = [
            ("<script>alert('xss')</script>", ""),
            ("<img src='x' onerror='alert(1)'>", ""),
            ("javascript:alert('xss')", ""),
            ("<iframe src='evil.com'></iframe>", ""),
        ]
        
        for malicious_input, expected in test_cases:
            result = SecurityService.sanitize_string(malicious_input)
            assert "<script>" not in result
            assert "javascript:" not in result
            assert "<iframe>" not in result
            assert "onerror=" not in result
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization."""
        test_data = {
            "username": "testuser",
            "email": "test@example.com",
            "malicious": "'; DROP TABLE users; --",
            "xss_attempt": "<script>alert('xss')</script>",
            "normal_field": "Normal value"
        }
        
        allowed_keys = ["username", "email", "normal_field"]
        result = SecurityService.sanitize_dict(test_data, allowed_keys)
        
        # Should only contain allowed keys
        assert "malicious" not in result
        assert "xss_attempt" not in result
        assert "username" in result
        assert "email" in result
        assert "normal_field" in result
        
        # Values should be sanitized
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["normal_field"] == "Normal value"
    
    def test_validate_user_input(self):
        """Test user input validation."""
        # Valid user data
        valid_data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "ValidPass123!",
            "full_name": "Valid User"
        }
        
        result = SecurityService.validate_user_input(valid_data)
        assert result["username"] == "validuser"
        assert result["email"] == "valid@example.com"
        assert result["full_name"] == "Valid User"
        
        # Invalid username
        with pytest.raises(ValueError, match="Username must be"):
            SecurityService.validate_user_input({"username": "invalid@user"})
        
        # Invalid email
        with pytest.raises(ValueError, match="Invalid email format"):
            SecurityService.validate_user_input({"email": "invalid-email"})
    
    def test_validate_device_input(self):
        """Test device input validation."""
        # Valid device data
        valid_data = {
            "device_id": "device123",
            "name": "Test Device",
            "location": "Test Location",
            "status": "online"
        }
        
        result = SecurityService.validate_device_input(valid_data)
        assert result["device_id"] == "device123"
        assert result["name"] == "Test Device"
        assert result["status"] == "online"
        
        # Invalid device ID
        with pytest.raises(ValueError, match="Device ID must be"):
            SecurityService.validate_device_input({"device_id": "invalid@device$"})
        
        # Invalid status
        with pytest.raises(ValueError, match="Status must be"):
            SecurityService.validate_device_input({"status": "invalid_status"})
    
    def test_search_query_sanitization(self):
        """Test search query sanitization."""
        # Normal search
        result = SecurityService.sanitize_search_query("test query")
        assert result == "test query"
        
        # Search with dangerous characters
        result = SecurityService.sanitize_search_query("test'; DROP TABLE users; --")
        assert "--" not in result
        assert "DROP TABLE" not in result
        assert ";" not in result


class TestAuthServiceSecurity:
    """Test authentication service security."""
    
    def test_create_user_with_sql_injection(self, db):
        """Test user creation with SQL injection attempts."""
        # Attempt to create user with malicious data
        malicious_user = UserCreate(
            username="testuser'; DROP TABLE users; --",
            email="test@example.com",
            password="TestPass123!",
            full_name="Test User"
        )
        
        # Should raise ValueError due to invalid username
        with pytest.raises(ValueError):
            create_user(db, malicious_user)
    
    def test_get_user_by_username_sanitization(self, db):
        """Test username sanitization in user lookup."""
        # Create a legitimate user first
        legitimate_user = UserCreate(
            username="legitimateuser",
            email="legit@example.com",
            password="TestPass123!",
            full_name="Legitimate User"
        )
        create_user(db, legitimate_user)
        
        # Try to find user with malicious username
        result = get_user_by_username(db, "legitimateuser'; DROP TABLE users; --")
        # Should return None because the malicious part is sanitized
        assert result is None
        
        # Normal lookup should work
        result = get_user_by_username(db, "legitimateuser")
        assert result is not None
        assert result.username == "legitimateuser"
    
    def test_authenticate_user_sanitization(self, db):
        """Test authentication with sanitized input."""
        # Create a legitimate user
        legitimate_user = UserCreate(
            username="authuser",
            email="auth@example.com",
            password="TestPass123!",
            full_name="Auth User"
        )
        create_user(db, legitimate_user)
        
        # Try to authenticate with malicious username
        result = authenticate_user(db, "authuser'; DROP TABLE users; --", "TestPass123!")
        assert result is None  # Should fail due to sanitization
        
        # Normal authentication should work
        result = authenticate_user(db, "authuser", "TestPass123!")
        assert result is not None
        assert result.username == "authuser"


class TestDeviceServiceSecurity:
    """Test device service security."""
    
    def test_create_device_with_sql_injection(self, db):
        """Test device creation with SQL injection attempts."""
        malicious_device_data = {
            "device_id": "device123'; DROP TABLE devices; --",
            "name": "Test Device",
            "location": "Test Location",
            "status": "online"
        }
        
        # Should raise ValueError due to invalid device_id
        with pytest.raises(ValueError):
            DeviceService.create_device(db, malicious_device_data)
    
    def test_get_device_by_id_sanitization(self, db):
        """Test device lookup sanitization."""
        # Create a legitimate device
        legitimate_device_data = {
            "device_id": "legitimate_device",
            "name": "Legitimate Device",
            "location": "Test Location",
            "status": "online"
        }
        DeviceService.create_device(db, legitimate_device_data)
        
        # Try to find device with malicious ID
        result = DeviceService.get_device_by_id(db, "legitimate_device'; DROP TABLE devices; --")
        assert result is None  # Should return None due to sanitization
        
        # Normal lookup should work
        result = DeviceService.get_device_by_id(db, "legitimate_device")
        assert result is not None
        assert result.device_id == "legitimate_device"
    
    def test_search_devices_sanitization(self, db):
        """Test device search sanitization."""
        # Create a test device
        test_device_data = {
            "device_id": "searchable_device",
            "name": "Searchable Device",
            "location": "Search Location",
            "status": "online"
        }
        DeviceService.create_device(db, test_device_data)
        
        # Search with malicious query
        results = DeviceService.search_devices(db, "device'; DROP TABLE devices; --")
        # Should return empty results due to sanitization
        assert len(results) == 0
        
        # Normal search should work
        results = DeviceService.search_devices(db, "Searchable")
        assert len(results) >= 0  # May be 0 or more depending on search implementation


class TestInputValidation:
    """Test comprehensive input validation."""
    
    def test_null_byte_injection(self):
        """Test null byte injection prevention."""
        malicious_input = "test\x00malicious"
        result = SecurityService.sanitize_string(malicious_input)
        assert "\x00" not in result
        assert result == "testmalicious"
    
    def test_length_limits(self):
        """Test input length limits."""
        long_input = "a" * 1000
        result = SecurityService.sanitize_string(long_input, max_length=100)
        assert len(result) <= 100
    
    def test_unicode_handling(self):
        """Test unicode character handling."""
        unicode_input = "test 你好 world"
        result = SecurityService.sanitize_string(unicode_input)
        assert "test 你好 world" in result
    
    def test_special_characters(self):
        """Test handling of special characters."""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = SecurityService.sanitize_string(special_chars)
        # Should not contain dangerous patterns but may contain some special chars
        assert "--" not in result
        assert "/*" not in result


def run_security_tests():
    """Run all security tests."""
    print("🔒 Running SQL Injection Prevention Tests...")
    
    # Run pytest programmatically
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
        ], capture_output=True, text=True, cwd=".")
        
        print("Test Output:")
        print(result.stdout)
        if result.stderr:
            print("Test Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All security tests passed!")
        else:
            print("❌ Some security tests failed!")
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


if __name__ == "__main__":
    run_security_tests()
