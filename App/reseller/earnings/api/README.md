# Reseller API

This directory contains API endpoints for the reseller module, providing programmatic access to earnings-related operations through AJAX and RESTful interfaces.

## API Structure

### API Version 1 (`v1/`) 🆕
Contains the new RESTful API implementation following Django REST Framework patterns.
- **Serializers**: Data serialization and validation
- **ViewSets**: Full CRUD operations for reseller profiles
- **Custom Actions**: Profile stats, payment method updates
- **URL Routing**: Clean RESTful endpoints

See `/v1/README.md` for detailed documentation.

### Views (`views.py`)
Contains API view functions that handle HTTP requests and return JSON responses.

**Current Endpoints:**

#### 1. Request Payout (`/reseller/api/payouts/request/`)
- **Method:** POST
- **Authentication:** Required
- **Purpose:** Submit a new payout request
- **Request Data:**
  ```json
  {
    "amount": "500.00",
    "payment_method": "bank_transfer",
    "bank_account_number": "123456789",
    "bank_routing_number": "987654321",
    "notes": "Monthly payout request"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Payout requested successfully."
  }
  ```

#### 2. Request Invoice (`/reseller/api/invoices/request/`)
- **Method:** POST
- **Authentication:** Required
- **Purpose:** Generate an invoice for approved commissions
- **Request Data:**
  ```json
  {
    "period": "last_month",
    "description": "Commission invoice for January 2024"
  }
  ```
- **Alternative for custom period:**
  ```json
  {
    "period": "custom",
    "from_date": "2024-01-01",
    "to_date": "2024-01-31",
    "description": "Custom period invoice"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Invoice generated successfully."
  }
  ```

### URLs (`urls.py`)
Defines the URL patterns for API endpoints with proper namespacing.

## Features

### 1. **Authentication**
- All endpoints require user authentication
- Automatically checks for reseller profile access

### 2. **Validation**
- Form-based validation for all inputs
- Clear error messages returned in JSON format

### 3. **Error Handling**
- Graceful error handling with meaningful messages
- HTTP status codes follow REST conventions

### 4. **AJAX Support**
- Designed for seamless AJAX integration
- Returns JSON responses for all operations

## Usage Examples

### JavaScript/jQuery
```javascript
// Request a payout
$.ajax({
    url: '/reseller/api/payouts/request/',
    method: 'POST',
    data: {
        amount: '500.00',
        payment_method: 'paypal',
        paypal_email: 'user@example.com',
        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
    },
    success: function(response) {
        if (response.success) {
            alert(response.message);
            location.reload();
        } else {
            alert('Error: ' + response.error);
        }
    }
});
```

### Fetch API
```javascript
// Request an invoice
fetch('/reseller/api/invoices/request/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: new URLSearchParams({
        period: 'last_month',
        description: 'Monthly commission invoice'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log(data.message);
    }
});
```

## Security Considerations

1. **CSRF Protection** - All POST requests require CSRF token
2. **Authentication** - Login required for all endpoints
3. **Authorization** - Only resellers can access their own data
4. **Input Validation** - All inputs validated before processing
5. **SQL Injection Protection** - Django ORM prevents SQL injection

## Future API Enhancements

1. **RESTful Resources** - Full CRUD operations for commissions, invoices, payouts
2. **Pagination** - Support for paginated list responses
3. **Filtering** - Advanced filtering options for data queries
4. **Webhooks** - Real-time notifications for status changes
5. **API Versioning** - Version management for backward compatibility
6. **Rate Limiting** - Prevent API abuse
7. **Documentation** - Swagger/OpenAPI documentation

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {}  // Optional data object
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message",
    "errors": {  // Optional field-specific errors
        "field_name": ["Error message"]
    }
}
```
