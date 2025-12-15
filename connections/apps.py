from django.apps import AppConfig


class ConnectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'connections'

    def ready(self):
        """Import signals when app is ready"""
        import connections.signals  # noqa: F401