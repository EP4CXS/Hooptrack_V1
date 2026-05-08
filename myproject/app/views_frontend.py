"""Backward-compatible import path for the frontend page view.

New code should import from `app.views.frontend`.
"""

from app.views.frontend import page_view  # noqa: F401
