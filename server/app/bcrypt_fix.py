"""
Workaround for bcrypt compatibility issue.
"""

import bcrypt
from passlib.context import CryptContext
from passlib.handlers.bcrypt import bcrypt as passlib_bcrypt
from passlib.utils import to_bytes, to_unicode


class FixedBcryptHandler(passlib_bcrypt):
    """
    Fixed bcrypt handler that works with newer bcrypt versions.
    """
    
    @classmethod
    def _load_backend_mixin(cls, name, dryrun=False):
        """Override the problematic version check."""
        if name == "bcrypt":
            import bcrypt as _bcrypt
            cls._bcrypt = _bcrypt
            return cls
        return super()._load_backend_mixin(name, dryrun)


# Register the fixed handler
from passlib.registry import register_crypt_handler
register_crypt_handler(FixedBcryptHandler, force=True)

# Create context with the fixed handler
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
