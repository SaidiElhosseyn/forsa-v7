# ── À AJOUTER DANS settings.py ──

INSTALLED_APPS = [
    # ... apps existantes ...
    'django.contrib.staticfiles',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],  # ← Ajouter BASE_DIR/templates
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

STATIC_URL  = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL          = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL= '/'

# ── Error handlers (dans urls.py principal) ──
# handler404 = 'core.views.error_404'
# handler500 = 'core.views.error_500'

# ── 404/500 views ──
# from django.shortcuts import render
# def error_404(request, exception): return render(request, 'errors/404.html', status=404)
# def error_500(request): return render(request, 'errors/500.html', status=500)
