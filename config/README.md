# EvolvePayments Project Structure

This is the main Django project configuration folder, organized for better maintainability and clarity.

## Folder Structure

```
EvolvePayments/
├── __init__.py          # Python package initialization
├── config/              # Configuration files
│   ├── settings.py      # Django settings configuration
│   └── urls.py          # Main URL routing configuration
└── deployment/          # Deployment-related files
    ├── asgi.py          # ASGI configuration for async deployment
    └── wsgi.py          # WSGI configuration for traditional deployment
```

## Folder Descriptions

### `config/`
Contains all configuration-related files:
- **settings.py**: All Django settings including database, middleware, installed apps, etc.
- **urls.py**: Main URL configuration that includes app-specific URLs

### `deployment/`
Contains deployment interface files:
- **asgi.py**: Asynchronous Server Gateway Interface config (for async Django)
- **wsgi.py**: Web Server Gateway Interface config (for traditional Django deployment)

## Important Updates

After reorganization, the following references were updated:

1. **manage.py**: 
   - `DJANGO_SETTINGS_MODULE` → `'EvolvePayments.config.settings'`

2. **settings.py**:
   - `ROOT_URLCONF` → `'EvolvePayments.config.urls'`
   - `WSGI_APPLICATION` → `'EvolvePayments.deployment.wsgi.application'`
   - `BASE_DIR` → Added one more `.parent` to account for new directory depth

3. **wsgi.py & asgi.py**:
   - `DJANGO_SETTINGS_MODULE` → `'EvolvePayments.config.settings'`

## Benefits

1. **Clear Separation**: Configuration and deployment files are now clearly separated
2. **Scalability**: Easy to add more configuration files (e.g., settings for different environments)
3. **Maintainability**: Related files are grouped together
4. **Best Practice**: Follows Django project organization best practices
