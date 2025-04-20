NSTALLED_APPS = [
    ...
    'voting',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Mobile Money API Settings (example for MTN)
MOMO_API_KEY = os.getenv('MOMO_API_KEY')
MOMO_USER_ID = os.getenv('MOMO_USER_ID')