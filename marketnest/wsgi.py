"""
WSGI config for MarketNest project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketnest.settings')
application = get_wsgi_application()
