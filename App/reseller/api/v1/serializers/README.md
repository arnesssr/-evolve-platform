# API v1 Serializers

This directory contains the serializers used by API Version 1 to handle data conversion, serialization, and deserialization for the reseller module.

## Serializer Components

**1. UserSerializer (`reseller_serializers.py`)**
- Serializes basic user information

**Key Features:**
- Provides `id`, `username`, `email`, and `full_name`
- Readonly fields

**2. ResellerSerializer (`reseller_serializers.py`)**
- Complete serialization of reseller profile
- Includes nested user details

**Key Features:**
- All reseller profile fields
- Includes `available_balance`, `tier_commission_rate`
- Full view with read-only fields for security

**3. ResellerProfileUpdateSerializer (`reseller_serializers.py`)**
- Allows updates to reseller profile fields

**Key Features:**
- Company, contact details update fields
- Validates phone number format

**4. PaymentMethodSerializer (`reseller_serializers.py`)**
- Manages the serialization of payment data

**Key Features:**
- Payment-type specific validation

**5. ResellerStatsSerializer (`reseller_serializers.py`)**
- Provides comprehensive reseller statistics

**Key Features:**
- Serializes sales, commissions, balance data

**6. ProfileCompletionSerializer (`reseller_serializers.py`)**
- Serializes profile completion status

**Key Features:**
- Converts completion percentage and required fields into JSON

**7. ResellerListSerializer (`reseller_serializers.py`)**
- Summarizes reseller list view

**Key Features:**
- Displays minimal, essential fields for listing

## Integration

These serializers are central to:
- **API endpoints**: Dealing with JSON requests and responses
- **Validation**: Ensuring data integrity when processing requests

## Benefits

1. **Consistency**: Ensures uniform data across API responses
2. **Security**: Exposes only necessary fields while securing sensitive data
3. **Flexibility**: Easily expanded to include additional fields

## Usage Patterns

```python
from .serializers.reseller_serializers import ResellerSerializer

serializer = ResellerSerializer(instance=reseller_instance)
data = serializer.data
```

## Future Enhancements

1. **Automated Tests**: Improve coverage for serialization logic
2. **Dynamic Fields**: Customize fields returned based on user roles
3. **Version Compatibility**: Support multiple serializer versions for legacy API users
4. **Schema Generation**: Use schema tools to auto-generate documentation
5. **Advanced Validation**: Implement complex validation for nested data

