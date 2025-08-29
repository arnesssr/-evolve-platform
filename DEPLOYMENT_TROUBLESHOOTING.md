# Deployment Troubleshooting Guide

## Current Issue: WhiteNoise Manifest Error

### The Error
```
ValueError: Missing staticfiles manifest entry for 'css/landing.css'
```

### What We've Done

1. **Fixed `.dockerignore`** - Removed `/static` exclusion so CSS source files are copied to Docker image
2. **Switched to Gunicorn** - Using production WSGI server instead of `runserver`
3. **Forced DEBUG=False** - Ensures production mode on Render
4. **Simplified WhiteNoise Storage** - Using basic `StaticFilesStorage` to avoid manifest complexity

### Current Configuration

#### WhiteNoise Settings:
```python
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MANIFEST_STRICT = False
```

#### Key Files:
- **Dockerfile**: Uses gunicorn, copies static files
- **start.sh**: Detailed logging, runs collectstatic with verbosity
- **settings.py**: Simplified storage, forced DEBUG=False on Render

### What to Watch in Render Logs

1. **Look for these success messages:**
   ```
   Production mode: DEBUG set to False on Render platform
   Static directory contents before collection:
   163 static files copied to '/app/staticfiles'
   Starting gunicorn server...
   ```

2. **Check for these potential issues:**
   - "No static directory found" - Docker build problem
   - "No staticfiles/css directory found" - Collection problem
   - Still using "Starting development server" - Not using gunicorn

### Testing After Deployment

1. **Main site**: https://evolve-platform.onrender.com/
2. **Diagnostic page**: https://evolve-platform.onrender.com/static-diagnostic/
3. **Test page**: https://evolve-platform.onrender.com/static-test/

### Next Steps If Issues Persist

If you still get the manifest error:

1. **Temporary Fix**: Set environment variable on Render:
   ```
   WHITENOISE_USE_FINDERS=True
   ```

2. **Alternative**: Remove WhiteNoise storage entirely and use Django's static serving:
   ```python
   # In settings.py for production
   STORAGES = {
       "staticfiles": {
           "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
       },
   }
   ```

3. **Check Render logs** for:
   - Static files being collected successfully
   - No 404s on /static/ URLs
   - Gunicorn starting (not runserver)

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 500 error with manifest | WhiteNoise can't find files | Use basic storage backend |
| CSS not loading | Files not copied to Docker | Check .dockerignore |
| Still in DEBUG mode | Environment not detected | Force DEBUG=False |
| Using runserver | Wrong Docker command | Use gunicorn in CMD |

### Recovery Plan

If the site is still broken, we can quickly revert to a working state:

1. **Disable WhiteNoise compression**:
   ```python
   WHITENOISE_USE_FINDERS = True
   WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['css', 'js']
   ```

2. **Use URL fallback in urls.py** (already implemented)

3. **Serve via Django** (debug mode only):
   ```python
   DEBUG = True  # Temporarily
   ```

The current deployment should work with basic static file serving via WhiteNoise.
