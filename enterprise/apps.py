from django.apps import AppConfig


class EnterpriseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'enterprise'
    verbose_name = 'Empresa'

    def ready(self):
        import enterprise.signals
        return super().ready()
