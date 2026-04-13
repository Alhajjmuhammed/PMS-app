# Settings package
import os

# Determine which settings to use based on environment
environment = os.environ.get('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    # Default to development
    from .development import *
