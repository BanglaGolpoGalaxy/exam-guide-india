"""
Admin Panel Blueprint
Provides admin-mode access to all public pages with inline editing controls.
"""
from flask import Blueprint

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin-panel'
)

from admin_panel import routes  # noqa: E402, F401 – registers routes onto blueprint
