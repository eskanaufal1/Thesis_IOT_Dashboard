# Security Implementation Guide

## Overview

This document outlines the comprehensive security measures implemented in the IoT Dashboard backend to prevent SQL injection attacks and ensure proper input sanitization.

## Table of Contents

1. [Security Architecture](#security-architecture)
2. [SQL Injection Prevention](#sql-injection-prevention)
3. [Input Sanitization](#input-sanitization)
4. [Secure Database Operations](#secure-database-operations)
5. [API Security](#api-security)
6. [Testing and Validation](#testing-and-validation)
7. [Best Practices](#best-practices)

## Security Architecture

### Core Components

1. **SecurityService**: Central service for all security operations
2. **Input Validation**: Comprehensive input validation and sanitization
3. **Safe Query Execution**: Secure database query execution wrapper
4. **Authentication**: JWT-based authentication with input sanitization
5. **Authorization**: Role-based access control

### File Structure

```
server/
├── services/
│   ├── security_service.py    # Main security service
│   ├── auth_service.py        # Authentication with security
│   ├── device_service.py      # Device management with security
│   └── database_service.py    # Database operations with security
├── api/
│   ├── auth.py               # Authentication endpoints
│   └── devices.py            # Device management endpoints
├── models/
│   ├── user.py               # User model
│   ├── database.py           # Database models
│   └── auth_schemas.py       # Authentication schemas
└── test_security.py          # Security tests
```

## SQL Injection Prevention

### Pattern Detection

The system detects and prevents common SQL injection patterns:

```python
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
```

### Prevention Methods

1. **Pattern Matching**: Detect and remove malicious SQL patterns
2. **Input Sanitization**: Clean all user inputs before processing
3. **Parameterized Queries**: Use SQLAlchemy ORM for safe query execution
4. **Length Limits**: Enforce maximum input lengths
5. **Character Filtering**: Remove dangerous characters

### Examples

```python
# Malicious input
malicious_input = "'; DROP TABLE users; --"

# After sanitization
clean_input = SecurityService.sanitize_string(malicious_input)
# Result: "" (empty string, dangerous parts removed)

# Safe database query
user = SecurityService.safe_query_execution(
    db,
    lambda db_session, username: db_session.query(User).filter(User.username == username).first(),
    clean_input
)
```

## Input Sanitization

### String Sanitization

```python
def sanitize_string(input_str: str, max_length: int = 255, allow_html: bool = False) -> str:
    """
    Comprehensive string sanitization:
    - Length limits
    - Null byte removal
    - SQL injection pattern detection
    - XSS pattern detection
    - HTML escaping
    - Whitespace normalization
    """
```

### Dictionary Sanitization

```python
def sanitize_dict(data: Dict[str, Any], allowed_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Recursive dictionary sanitization:
    - Key validation
    - Value sanitization
    - Type checking
    - Recursive processing
    """
```

### Specialized Validation

#### User Input Validation

```python
def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    User-specific validation:
    - Username: alphanumeric + underscore, 3-50 chars
    - Email: proper email format validation
    - Phone: digits, spaces, and basic punctuation
    """
```

#### Device Input Validation

```python
def validate_device_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Device-specific validation:
    - Device ID: alphanumeric + hyphen/underscore, 1-50 chars
    - Status: limited to 'online', 'offline', 'maintenance'
    - Relay states: limited to 'on', 'off'
    """
```

## Secure Database Operations

### Safe Query Execution

All database operations use the `safe_query_execution` wrapper:

```python
def safe_query_execution(db: Session, query_func, *args, **kwargs):
    """
    Safe query execution with:
    - Exception handling
    - Automatic rollback on errors
    - Logging of security events
    """
```

### Usage Examples

```python
# User lookup
user = SecurityService.safe_query_execution(
    db,
    lambda db_session, username: db_session.query(User).filter(User.username == username).first(),
    sanitized_username
)

# Device creation
device = SecurityService.safe_query_execution(
    db,
    lambda db_session, device_obj: _create_device_transaction(db_session, device_obj),
    validated_device
)
```

### Transaction Management

```python
def _create_device_transaction(db: Session, device: Device) -> Device:
    """
    Atomic transaction for device creation:
    - Add to session
    - Commit changes
    - Refresh object
    - Return result
    """
    db.add(device)
    db.commit()
    db.refresh(device)
    return device
```

## API Security

### Authentication

All API endpoints require authentication:

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    JWT token validation with:
    - Token verification
    - User lookup
    - Input sanitization
    """
```

### Input Validation at API Level

```python
@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User update with:
    - Input sanitization
    - Field validation
    - Safe query execution
    - Error handling
    """
```

### Device Management Security

```python
@router.post("/", response_model=dict)
async def create_device(
    device_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Device creation with:
    - Authentication required
    - Input validation
    - Sanitization
    - Safe database operations
    """
```

## XSS Prevention

### Pattern Detection

```python
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
```

### HTML Escaping

```python
# Automatic HTML escaping for user inputs
sanitized = html.escape(user_input)
```

## Testing and Validation

### Security Test Suite

The `test_security.py` file contains comprehensive tests:

1. **String Sanitization Tests**
   - Basic string cleaning
   - SQL injection pattern detection
   - XSS pattern detection
   - Length limits

2. **Dictionary Sanitization Tests**
   - Key validation
   - Value sanitization
   - Recursive processing

3. **Input Validation Tests**
   - User input validation
   - Device input validation
   - Error handling

4. **Service Security Tests**
   - Authentication service security
   - Device service security
   - Database operation security

### Running Tests

```bash
# Run security tests
python test_security.py

# Run with pytest
pytest test_security.py -v

# Run specific test class
pytest test_security.py::TestSecurityService -v
```

## Best Practices

### 1. Input Validation

- **Always validate** user inputs before processing
- **Use whitelisting** approach for allowed characters
- **Implement length limits** for all string inputs
- **Sanitize recursively** for nested data structures

### 2. Database Operations

- **Use parameterized queries** with SQLAlchemy ORM
- **Wrap all queries** with safe execution handlers
- **Implement proper transactions** with rollback on errors
- **Log security events** for monitoring

### 3. Authentication and Authorization

- **Sanitize credentials** before authentication
- **Use JWT tokens** for stateless authentication
- **Implement role-based access control**
- **Validate tokens** on every request

### 4. Error Handling

- **Never expose** database errors to users
- **Log security incidents** for analysis
- **Return generic error messages** to prevent information disclosure
- **Implement proper exception handling**

### 5. Monitoring and Logging

- **Log all security events** (injection attempts, validation failures)
- **Monitor for patterns** in security incidents
- **Set up alerts** for suspicious activity
- **Regular security audits** of logs

## Security Headers

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Content Security Policy

Implement CSP headers in production:

```python
# Example CSP header
"Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
```

## Deployment Security

### Environment Variables

```bash
# Production environment variables
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/iot_dashboard
JWT_SECRET_KEY=another-very-secure-jwt-key
```

### Database Security

- Use **strong passwords** for database connections
- Implement **database user permissions** (least privilege)
- Enable **database logging** for security events
- Regular **database backups** with encryption

### Network Security

- Use **HTTPS** in production
- Implement **rate limiting** for API endpoints
- Use **reverse proxy** (nginx/Apache) for additional security
- **Firewall rules** to restrict database access

## Conclusion

The IoT Dashboard backend implements comprehensive security measures to prevent SQL injection attacks and ensure proper input sanitization. The multi-layered approach includes:

1. **Input validation** at multiple levels
2. **SQL injection prevention** through pattern detection
3. **XSS protection** through output encoding
4. **Safe database operations** with proper error handling
5. **Authentication and authorization** with JWT tokens
6. **Comprehensive testing** to validate security measures

Regular security audits and updates are recommended to maintain the security posture of the application.
