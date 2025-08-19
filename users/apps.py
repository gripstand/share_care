from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

# your_app/apps.py


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals  # This line registers the signals