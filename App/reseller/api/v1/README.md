# API Version 1

This directory contains the RESTful API implementation for the reseller module, following Django REST Framework patterns.

## Structure

```
v1/
├── __init__.py
├── serializers/          # Data serialization
│   ├── __init__.py
│   └── reseller_serializers.py
├── views/               # API endpoints
│   ├── __init__.py
│   └── reseller_views.py
└── urls.py             # API routing
```

## API Endpoints

### Reseller Profile Endpoints

Base URL: `/api/v1/resellers/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all resellers (staff only) |
| POST | `/` | Create reseller profile |
| GET | `/{id}/` | Get specific reseller profile |
| PUT | `/{id}/` | Update entire profile |
| PATCH | `/{id}/` | Partial profile update |
| DELETE | `/{id}/` | Delete reseller profile |
| GET | `/my_profile/` | Get authenticated user's profile |
| PUT | `/{id}/update_profile/` | Update profile information |
| PUT | `/{id}/update_payment_method/` | Update payment method |
| GET | `/{id}/stats/` | Get reseller statistics |

## Authentication

All endpoints require authentication using:
- Token Authentication
- Session Authentication (for web interface)

## Permissions

- Regular users can only access their own profile
- Staff users can access all profiles
- Profile creation requires authenticated user without existing profile

## Response Format

### Success Response
```json
{
    "id": 1,
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe"
    },
    "company_name": "ABC Company",
    "referral_code": "ABC123",
    "tier": "GOLD",
    "commission_rate": "20.00",
    "is_verified": true,
    // ... other fields
}
```

### Error Response
```json
{
    "detail": "Error message",
    "field_errors": {
        "field_name": ["Error details"]
    }
}
```

## Usage Examples

### Create Profile
```bash
curl -X POST http://localhost:8000/api/v1/resellers/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "My Company",
    "phone_number": "+1234567890",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "payment_method": "bank_transfer",
    "bank_account_name": "John Doe",
    "bank_account_number": "123456789",
    "bank_name": "Example Bank"
  }'
```

### Get My Profile
```bash
curl -X GET http://localhost:8000/api/v1/resellers/my_profile/ \
  -H "Authorization: Token your-token"
```

### Update Payment Method
```bash
curl -X PUT http://localhost:8000/api/v1/resellers/1/update_payment_method/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "paypal",
    "paypal_email": "john@paypal.com"
  }'
```

## Integration

- **Frontend**: JavaScript/React applications can consume these endpoints
- **Mobile Apps**: Native apps can use the API for reseller features
- **Third-party**: External systems can integrate using API tokens

## Versioning

This is API version 1. Future versions will be in separate directories (v2, v3, etc.) to maintain backward compatibility.

## Future Enhancements

1. **GraphQL Support**: Add GraphQL endpoint for flexible queries
2. **Webhooks**: Notify external systems of profile changes
3. **Rate Limiting**: Implement API rate limits
4. **API Documentation**: Generate OpenAPI/Swagger docs
