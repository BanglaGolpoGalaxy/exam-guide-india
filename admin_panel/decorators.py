"""
Admin authentication decorators.
"""
import functools
from flask import session, redirect, url_for, flash


def admin_required(f):
    """Redirect to admin login if the session is not authenticated."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated
