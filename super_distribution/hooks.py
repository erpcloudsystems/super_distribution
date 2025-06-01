from . import __version__ as app_version

app_name = "super_distribution"
app_title = "Super Distribution"
app_publisher = "Tech Station"
app_description = "customization for erpnext"
app_email = "info@techstation.com.eg"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/super_distribution/css/super_distribution.css"
# app_include_js = "/assets/super_distribution/js/super_distribution.js"

# include js, css files in header of web template
# web_include_css = "/assets/super_distribution/css/super_distribution.css"
# web_include_js = "/assets/super_distribution/js/super_distribution.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "super_distribution/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    # "Sales Order" : "public/js/sales_order.js",
    # "Sales Invoice": "public/js/sales_invoice.js",
	"Sales Order" : "doctype_triggers/selling/sales_order/sales_order.js",
    "Sales Invoice" : "doctype_triggers/accounting/sales_invoice/sales_invoice.js",
	"Delivery Note" : "doctype_triggers/stock/delivery_note/delivery_note.js",
    "Sales Person": "public/js/sales_person.js",
    "Customer": "public/js/customer.js",
    "Purchase Invoice": "public/js/purchase_invoice.js",
    "Purchase Order": "public/js/purchase_order.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "super_distribution.utils.jinja_methods",
#	"filters": "super_distribution.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "super_distribution.install.before_install"
# after_install = "super_distribution.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "super_distribution.uninstall.before_uninstall"
# after_uninstall = "super_distribution.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "super_distribution.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Sales Order": "super_distribution.overrides.selling.sales_order.CustomSalesOrder",
	"Sales Invoice": "super_distribution.overrides.accounting.sales_invoice.CustomSalesInvoice",
	"Delivery Note": "super_distribution.overrides.stock.delivery_note.CustomDeliveryNote",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Order": {
		"before_insert": "super_distribution.doctype_triggers.selling.sales_order.sales_order.before_insert",
		"after_insert": "super_distribution.doctype_triggers.selling.sales_order.sales_order.after_insert",
		"onload": "super_distribution.doctype_triggers.selling.sales_order.sales_order.onload",
		"before_validate": "super_distribution.doctype_triggers.selling.sales_order.sales_order.before_validate",
		"validate": "super_distribution.doctype_triggers.selling.sales_order.sales_order.validate",
		"on_submit": "super_distribution.doctype_triggers.selling.sales_order.sales_order.on_submit",
		"on_cancel": "super_distribution.doctype_triggers.selling.sales_order.sales_order.on_cancel",
		"on_update_after_submit": "super_distribution.doctype_triggers.selling.sales_order.sales_order.on_update_after_submit",
		"before_save": "super_distribution.doctype_triggers.selling.sales_order.sales_order.before_save",
		"before_cancel": "super_distribution.doctype_triggers.selling.sales_order.sales_order.before_cancel",
		"on_update": "super_distribution.doctype_triggers.selling.sales_order.sales_order.on_update",
	},
	"Sales Invoice": {
		"before_insert": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.before_insert",
		"after_insert": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.after_insert",
		"onload": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.onload",
		"before_validate": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.before_validate",
		"validate": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.validate",
		"on_submit": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.on_submit",
		"on_cancel": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.on_cancel",
		"on_update_after_submit": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.on_update_after_submit",
		"before_save": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.before_save",
		"before_cancel": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.before_cancel",
		"on_update": "super_distribution.doctype_triggers.accounting.sales_invoice.sales_invoice.on_update",
	},
	"Delivery Note": {
		"before_insert": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.before_insert",
		"after_insert": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.after_insert",
		"onload": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.onload",
		"before_validate": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.before_validate",
		"validate": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.validate",
		"on_submit": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.on_submit",
		"on_cancel": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.on_cancel",
		"on_update_after_submit": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.on_update_after_submit",
		"before_save": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.before_save",
		"before_cancel": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.before_cancel",
		"on_update": "super_distribution.doctype_triggers.stock.delivery_note.delivery_note.on_update",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"super_distribution.tasks.all"
#	],
#	"daily": [
#		"super_distribution.tasks.daily"
#	],
#	"hourly": [
#		"super_distribution.tasks.hourly"
#	],
#	"weekly": [
#		"super_distribution.tasks.weekly"
#	],
#	"monthly": [
#		"super_distribution.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "super_distribution.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "super_distribution.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "super_distribution.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["super_distribution.utils.before_request"]
# after_request = ["super_distribution.utils.after_request"]

# Job Events
# ----------
# before_job = ["super_distribution.utils.before_job"]
# after_job = ["super_distribution.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"super_distribution.auth.validate"
# ]
