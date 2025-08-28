import os
import sys
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from pathlib import Path
from django.contrib.staticfiles.finders import find
from django.contrib.staticfiles import finders

@never_cache
def static_diagnostic_view(request):
    """Diagnostic view to help debug static file serving issues"""
    
    diagnostics = {
        'debug': settings.DEBUG,
        'static_url': settings.STATIC_URL,
        'static_root': str(settings.STATIC_ROOT),
        'staticfiles_dirs': [str(d) for d in settings.STATICFILES_DIRS],
        'middleware': settings.MIDDLEWARE,
        'whitenoise_installed': 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE,
        'staticfiles_storage': str(settings.STORAGES.get('staticfiles', {}).get('BACKEND', 'Not configured')),
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'environment': {
            'RENDER': 'RENDER' in os.environ,
            'RENDER_EXTERNAL_HOSTNAME': os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'Not set'),
            'RENDER_EXTERNAL_URL': os.environ.get('RENDER_EXTERNAL_URL', 'Not set'),
            'PORT': os.environ.get('PORT', 'Not set'),
        }
    }
    
    # Check if static root exists and has files
    static_root_path = Path(settings.STATIC_ROOT)
    diagnostics['static_root_exists'] = static_root_path.exists()
    diagnostics['static_root_is_dir'] = static_root_path.is_dir() if static_root_path.exists() else False
    
    if static_root_path.exists() and static_root_path.is_dir():
        # Count CSS files in staticfiles
        css_files = list(static_root_path.rglob('*.css'))
        diagnostics['css_files_count'] = len(css_files)
        diagnostics['sample_css_files'] = [str(f.relative_to(static_root_path)) for f in css_files[:5]]
    
    # Check if the auth.css file specifically exists
    auth_css_path = static_root_path / 'css' / 'auth.css'
    diagnostics['auth_css_exists'] = auth_css_path.exists()
    diagnostics['auth_css_path'] = str(auth_css_path)
    
    # Test URL generation
    try:
        from django.templatetags.static import static
        diagnostics['static_url_example'] = static('css/auth.css')
    except Exception as e:
        diagnostics['static_url_error'] = str(e)
    
    # Check if Django can find the file
    auth_css_finder = find('css/auth.css')
    diagnostics['auth_css_found_by_finder'] = auth_css_finder is not None
    if auth_css_finder:
        diagnostics['auth_css_finder_path'] = str(auth_css_finder)
    
    # Check STATICFILES_STORAGE setting
    diagnostics['staticfiles_storage_setting'] = getattr(settings, 'STATICFILES_STORAGE', 'Not set')
    
    # Check if we're using old or new storage config
    diagnostics['using_storages_config'] = hasattr(settings, 'STORAGES')
    
    # Python version
    diagnostics['python_version'] = sys.version
    
    # WhiteNoise version check
    try:
        import whitenoise
        diagnostics['whitenoise_version'] = whitenoise.__version__
    except:
        diagnostics['whitenoise_version'] = 'Not installed or error'
    
    return JsonResponse(diagnostics, json_dumps_params={'indent': 2})
