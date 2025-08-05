# Copyright (c) 2025, Sourav Singh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_fullname


class QuickNote(Document):
    def before_save(self):
        self.last_edited_by = frappe.session.user
        self.last_edited_at = now()
        self.owner_full_name = get_fullname(self.owner)

    def validate(self):
        self.validate_sharing_permissions()

    def validate_sharing_permissions(self):
        """Validate that users being shared with exist and have proper permissions"""
        for share in self.shared_with:
            if not frappe.db.exists("User", share.user):
                frappe.throw(f"User {share.user} does not exist")

    def can_read(self, user=None):
        """Check if user can read this note"""
        if not user:
            user = frappe.session.user

        # Owner can always read
        if self.owner == user:
            return True

        # Check if public
        if self.is_public:
            return True

        # Check if shared
        for share in self.shared_with:
            if share.user == user:
                return True

        return False

    def can_write(self, user=None):
        """Check if user can write to this note"""
        if not user:
            user = frappe.session.user

        # Owner can always write
        if self.owner == user:
            return True

        # Check sharing permissions
        for share in self.shared_with:
            if share.user == user and share.permission_level in ["Write", "Admin"]:
                return True

        return False

    def get_active_users(self):
        """Get list of users currently editing this note"""
        return frappe.cache().get_value(f"quicknotes:active_users:{self.name}") or []

    def add_active_user(self, user=None):
        """Add user to active editors list"""
        if not user:
            user = frappe.session.user

        cache_key = f"quicknotes:active_users:{self.name}"
        active_users = self.get_active_users()

        if user not in active_users:
            active_users.append(user)
            frappe.cache().set_value(cache_key, active_users, expires_in_sec=300)

    def remove_active_user(self, user=None):
        """Remove user from active editors list"""
        if not user:
            user = frappe.session.user

        cache_key = f"quicknotes:active_users:{self.name}"
        active_users = self.get_active_users()

        if user in active_users:
            active_users.remove(user)
            frappe.cache().set_value(cache_key, active_users, expires_in_sec=300)
