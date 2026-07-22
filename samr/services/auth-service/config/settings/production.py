from .base import *

DEBUG = False
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOST', 'localhost').split(',') if h.strip()]
