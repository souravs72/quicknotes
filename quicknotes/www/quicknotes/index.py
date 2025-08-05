import frappe


def get_context(context):
    context.title = "QuickNotes"
    context.show_sidebar = False

    # Ensure user is logged in
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    return context
