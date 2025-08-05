import frappe
from frappe import _
from frappe.utils import now, get_fullname
import json


@frappe.whitelist()
def get_my_notes():
    """Get all notes accessible to current user"""
    user = frappe.session.user

    # Notes owned by user
    owned_notes = frappe.get_all(
        "Quick Note",
        filters={"owner": user},
        fields=["name", "title", "modified", "last_edited_by", "is_public", "tags"],
    )

    # Notes shared with user
    shared_note_names = frappe.get_all(
        "Quick Note Share", filters={"user": user}, fields=["parent"]
    )

    shared_notes = []
    if shared_note_names:
        shared_notes = frappe.get_all(
            "Quick Note",
            filters={"name": ["in", [s.parent for s in shared_note_names]]},
            fields=[
                "name",
                "title",
                "modified",
                "last_edited_by",
                "is_public",
                "tags",
                "owner",
            ],
        )

    # Public notes (excluding owned ones)
    public_notes = frappe.get_all(
        "Quick Note",
        filters={"is_public": 1, "owner": ["!=", user]},
        fields=[
            "name",
            "title",
            "modified",
            "last_edited_by",
            "is_public",
            "tags",
            "owner",
        ],
    )

    return {"owned": owned_notes, "shared": shared_notes, "public": public_notes}


@frappe.whitelist()
def get_note(note_name):
    """Get note content with permission check"""
    doc = frappe.get_doc("Quick Note", note_name)

    if not doc.can_read():
        frappe.throw(_("You don't have permission to read this note"))

    # Add user to active editors
    doc.add_active_user()

    return {
        "name": doc.name,
        "title": doc.title,
        "content": doc.content,
        "content_delta": doc.content_delta,
        "is_public": doc.is_public,
        "tags": doc.tags,
        "owner": doc.owner,
        "owner_full_name": doc.owner_full_name,
        "last_edited_by": doc.last_edited_by,
        "last_edited_at": doc.last_edited_at,
        "shared_with": doc.shared_with,
        "can_write": doc.can_write(),
        "active_users": doc.get_active_users(),
    }


@frappe.whitelist()
def save_note_content(note_name, content, content_delta=None):
    """Save note content with real-time sync"""
    doc = frappe.get_doc("Quick Note", note_name)

    if not doc.can_write():
        frappe.throw(_("You don't have permission to edit this note"))

    doc.content = content
    if content_delta:
        doc.content_delta = content_delta

    doc.save()

    # Emit real-time update
    emit_note_update(
        note_name,
        {
            "content": content,
            "content_delta": content_delta,
            "last_edited_by": frappe.session.user,
            "last_edited_at": now(),
        },
    )

    return {"success": True}


@frappe.whitelist()
def share_note(note_name, user_email, permission_level="Read"):
    """Share note with another user"""
    doc = frappe.get_doc("Quick Note", note_name)

    # Check if current user can share (owner or admin permission)
    if doc.owner != frappe.session.user:
        user_permission = None
        for share in doc.shared_with:
            if share.user == frappe.session.user:
                user_permission = share.permission_level
                break

        if user_permission != "Admin":
            frappe.throw(_("You don't have permission to share this note"))

    # Check if user exists
    if not frappe.db.exists("User", user_email):
        frappe.throw(_("User does not exist"))

    # Check if already shared
    for share in doc.shared_with:
        if share.user == user_email:
            share.permission_level = permission_level
            share.shared_on = now()  # Update timestamp
            doc.save()
            return {"success": True, "message": "Permission updated"}

    # Add new share
    doc.append(
        "shared_with",
        {"user": user_email, "permission_level": permission_level, "shared_on": now()},
    )
    doc.save()

    return {"success": True, "message": "Note shared successfully"}


@frappe.whitelist()
def create_note(title, content="", is_public=0):
    """Create a new note"""
    doc = frappe.get_doc(
        {
            "doctype": "Quick Note",
            "title": title,
            "content": content,
            "is_public": is_public,
        }
    )
    doc.insert()

    return {"name": doc.name, "title": doc.title}


@frappe.whitelist()
def join_note_session(note_name):
    """Join a note editing session"""
    doc = frappe.get_doc("Quick Note", note_name)

    if not doc.can_read():
        frappe.throw(_("You don't have permission to access this note"))

    doc.add_active_user()

    # Emit user joined event
    emit_user_joined(note_name, frappe.session.user)

    return {"success": True}


@frappe.whitelist()
def leave_note_session(note_name):
    """Leave a note editing session"""
    doc = frappe.get_doc("Quick Note", note_name)
    doc.remove_active_user()

    # Emit user left event
    emit_user_left(note_name, frappe.session.user)

    return {"success": True}


def emit_note_update(note_name, data):
    """Emit real-time note update via socketio"""
    frappe.publish_realtime(
        event="note_updated",
        message={"note_name": note_name, "data": data, "user": frappe.session.user},
        room=f"note:{note_name}",
    )


def emit_user_joined(note_name, user):
    """Emit user joined event"""
    frappe.publish_realtime(
        event="user_joined",
        message={
            "note_name": note_name,
            "user": user,
            "user_full_name": get_fullname(user),
        },
        room=f"note:{note_name}",
    )


def emit_user_left(note_name, user):
    """Emit user left event"""
    frappe.publish_realtime(
        event="user_left",
        message={"note_name": note_name, "user": user},
        room=f"note:{note_name}",
    )


def note_updated(doc, method):
    """Hook called when note is updated"""
    pass


def note_created(doc, method):
    """Hook called when note is created"""
    pass
