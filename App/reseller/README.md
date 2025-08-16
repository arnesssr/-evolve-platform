# Reseller App Architecture

## Overview
The reseller functionality has been implemented as a separate Django app with its own views and URL patterns.

## Why Separate App Architecture

### 1. **Modularity**
- Keeps reseller-specific logic isolated from other parts of the application
- Easier to maintain and update without affecting other modules

### 2. **Scalability**
- Can be easily extended with additional reseller features
- Can be deployed independently if needed in the future

### 3. **Clear Separation of Concerns**
- Reseller views handle only reseller-related requests
- URL patterns are namespaced under 'reseller:' for clarity

## Current Implementation

### URLs
- All reseller URLs are prefixed with `/reseller/`
- URL names are namespaced as `reseller:name`
- Examples: `reseller:dashboard`, `reseller:leads`, `reseller:commissions`

### Views
- Each view corresponds to a specific reseller page
- Views render templates from `templates/dashboards/reseller/`
- Currently returns mock data for demonstration

## Benefits
1. **Easy to extend** - Add new reseller features without touching core app
2. **Reusable** - Can be packaged and used in other projects
3. **Testing** - Isolated testing of reseller functionality
4. **Permissions** - Easy to apply reseller-specific permissions
