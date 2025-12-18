"""
Django App Configuration for Persistence
"""
from django.apps import AppConfig


class PersistenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.infrastructure.persistence'
    label = 'persistence'
    verbose_name = 'LMS Persistence'
    
    def ready(self):
        # Import signals if needed
        pass

