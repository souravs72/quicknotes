import frappe
from frappe.utils import now_datetime, add_to_date


def cleanup_inactive_sessions():
    """Clean up inactive user sessions from cache"""
    # This runs every 5 minutes to clean up stale active user sessions
    cache = frappe.cache()

    # Get all active session keys
    pattern = "quicknotes:active_users:*"
    keys = cache.get_keys(pattern)

    for key in keys:
        # For now, we rely on cache expiration (5 minutes)
        # In a more sophisticated implementation, you could track last activity
        pass
