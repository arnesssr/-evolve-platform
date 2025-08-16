"""Base service class."""
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class BaseService:
    """Base service class with common functionality."""
    
    def __init__(self):
        self.logger = logger
    
    def log_info(self, message, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)
    
    def log_warning(self, message, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    @transaction.atomic
    def execute_in_transaction(self, func, *args, **kwargs):
        """Execute function in database transaction."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.log_error(f"Transaction failed: {str(e)}")
            raise
    
    def validate_positive_amount(self, amount, field_name='amount'):
        """Validate that amount is positive."""
        if amount <= 0:
            raise ValidationError(f"{field_name} must be positive")
        return True
    
    def validate_required_fields(self, data, required_fields):
        """Validate that all required fields are present."""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        return True
