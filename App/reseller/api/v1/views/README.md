# API v1 Views

This directory contains the API view implementations using Django REST Framework viewsets and custom actions.

## View Components

### ResellerViewSet (`reseller_views.py`) 🆕

A comprehensive viewset for managing reseller profiles through RESTful API endpoints.

**Base Features:**
- Full CRUD operations (Create, Read, Update, Delete)
- Authentication required for all endpoints
- Automatic filtering based on user permissions

**Custom Actions:**

#### `my_profile`
- **Method**: GET
- **URL**: `/api/v1/resellers/my_profile/`
- **Description**: Retrieves the authenticated user's reseller profile
- **Returns**: ResellerSerializer data or 404 if no profile exists

#### `update_profile`
- **Method**: PUT
- **URL**: `/api/v1/resellers/{id}/update_profile/`
- **Description**: Updates reseller profile information
- **Body**: Profile fields to update
- **Validation**: Uses ResellerProfileUpdateSerializer

#### `update_payment_method`
- **Method**: PUT
- **URL**: `/api/v1/resellers/{id}/update_payment_method/`
- **Description**: Updates payment method configuration
- **Body**: Payment method and related fields
- **Validation**: Conditional based on payment type

#### `stats`
- **Method**: GET
- **URL**: `/api/v1/resellers/{id}/stats/`
- **Description**: Returns comprehensive statistics for a reseller
- **Returns**: Sales, commissions, and profile completion data

## Permission Logic

```python
def get_queryset(self):
    user = self.request.user
    
    # Regular users see only their profile
    if not user.is_staff:
        return self.queryset.filter(user=user)
    
    # Staff users see all profiles
    return self.queryset
```

## Usage Examples

### Python/Django
```python
from myapp.reseller.api.v1.views.reseller_views import ResellerViewSet

# In URLs
router.register(r'resellers', ResellerViewSet, basename='reseller')
```

### JavaScript/Axios
```javascript
// Get my profile
const response = await axios.get('/api/v1/resellers/my_profile/', {
    headers: { 'Authorization': `Token ${authToken}` }
});

// Update profile
const updateData = {
    company_name: 'New Company Name',
    phone_number: '+1234567890'
};
await axios.put(`/api/v1/resellers/${id}/update_profile/`, updateData, {
    headers: { 'Authorization': `Token ${authToken}` }
});
```

## Error Handling

The viewset provides standard error responses:
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (no authentication)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (profile doesn't exist)

## Integration Points

- **Serializers**: Uses multiple serializers for different operations
- **Services**: Leverages ResellerService for business logic
- **Models**: Direct access to Reseller model for queries

## Best Practices

1. **Validation**: Always validate input using serializers
2. **Permissions**: Check user permissions before operations
3. **Error Messages**: Provide clear, actionable error messages
4. **Documentation**: Keep API documentation up-to-date
5. **Testing**: Write comprehensive tests for all endpoints

## Future Enhancements

1. **Filtering**: Add query parameter filtering
2. **Pagination**: Implement cursor-based pagination
3. **Caching**: Add Redis caching for frequently accessed data
4. **Throttling**: Implement rate limiting per user
5. **Audit Trail**: Log all API operations
