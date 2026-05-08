"""
Django app configuration for the Core app.

This app serves as the main application container for all business domains:
- Authentication
- Admin
- User management
- Business logic layers (services, selectors, requests)
- REST API
- Forms and validation
- Utils and middleware
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Application configuration for the Core app.

    Provides a central container for all domain-specific modules.
    The Core app is the primary application containing authentication,
    admin, and user domains with their respective models, views,
    services, and API endpoints.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        """
        Perform initialization when the app is ready.

        Import signals to ensure they are registered.
        """
        import app.signals  # noqa
        # #region agent log
        try:
            from app.utils.debug_agent_log import agent_debug_log

            agent_debug_log(
                hypothesis_id="boot",
                message="django_app_ready",
                data={"app": self.name},
                location="app.apps.CoreConfig.ready",
            )
        except Exception as exc:
            import sys

            print(f"DEBUG66881E:boot_log_failed:{exc!s}", file=sys.stderr, flush=True)
        # #endregion
