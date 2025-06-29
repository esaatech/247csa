from django.apps import AppConfig


class TeamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team'
    verbose_name = 'Team Management'

    def ready(self):
        import team.signals  # Import the signals
