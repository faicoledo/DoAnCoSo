# Settings package
from .base import *

# Import environment-specific settings
import os

env = os.environ.get('DJANGO_ENV', 'dev')

if env == 'prod':
    from .prod import *
else:
    from .dev import *

