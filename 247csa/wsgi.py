"""
WSGI config for 247csa project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '247csa.settings')

application = get_wsgi_application() 