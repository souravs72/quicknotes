app_name = "quicknotes"
app_title = "QuickNotes"
app_publisher = "Sourav Singh"
app_description = "Real-time collaborative note-taking app"
app_icon = "octicon octicon-file-text"
app_color = "grey"
app_email = "sourav@clapgrow.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "quicknotes",
# 		"logo": "/assets/quicknotes/logo.png",
# 		"title": "QuickNotes",
# 		"route": "/quicknotes",
# 		"has_permission": "quicknotes.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

app_include_css = "/assets/quicknotes/css/quicknotes.css"
app_include_js = "/assets/quicknotes/js/quicknotes.bundle.js"

# include js, css files in header of desk.html
# app_include_css = "/assets/quicknotes/css/quicknotes.css"
# app_include_js = "/assets/quicknotes/js/quicknotes.js"

# include js, css files in header of web template
# web_include_css = "/assets/quicknotes/css/quicknotes.css"
# web_include_js = "/assets/quicknotes/js/quicknotes.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "quicknotes/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
website_context = {
    "favicon": "/assets/quicknotes/images/favicon.png",
    "splash_image": "/assets/quicknotes/images/splash.png",
}
# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "quicknotes/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "quicknotes.utils.jinja_methods",
# 	"filters": "quicknotes.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "quicknotes.install.before_install"
# after_install = "quicknotes.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "quicknotes.uninstall.before_uninstall"
# after_uninstall = "quicknotes.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "quicknotes.utils.before_app_install"
# after_app_install = "quicknotes.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "quicknotes.utils.before_app_uninstall"
# after_app_uninstall = "quicknotes.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "quicknotes.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "Quick Note": {
        "on_update": "quicknotes.quicknotes.api.note_updated",
        "after_insert": "quicknotes.quicknotes.api.note_created",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"quicknotes.tasks.all"
# 	],
# 	"daily": [
# 		"quicknotes.tasks.daily"
# 	],
# 	"hourly": [
# 		"quicknotes.tasks.hourly"
# 	],
# 	"weekly": [
# 		"quicknotes.tasks.weekly"
# 	],
# 	"monthly": [
# 		"quicknotes.tasks.monthly"
# 	],
# }

scheduler_events = {
    "cron": {"0/5 * * * *": ["quicknotes.quicknotes.tasks.cleanup_inactive_sessions"]}
}

# Testing
# -------

# before_tests = "quicknotes.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "quicknotes.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "quicknotes.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["quicknotes.utils.before_request"]
# after_request = ["quicknotes.utils.after_request"]

# Job Events
# ----------
# before_job = ["quicknotes.utils.before_job"]
# after_job = ["quicknotes.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"quicknotes.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
