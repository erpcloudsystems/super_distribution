from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def before_insert(doc, method=None):
    pass
@frappe.whitelist()
def after_insert(doc, method=None):
    pass
@frappe.whitelist()
def onload(doc, method=None):
    pass
@frappe.whitelist()
def before_validate(doc, method=None):
    pass

@frappe.whitelist()
def validate(doc, method=None):
    # Calculate shipping and cash discount 
    calculate_additional_discount(doc)
    
@frappe.whitelist()
def on_submit(doc, method=None):
    pass
@frappe.whitelist()
def on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def before_save(doc, method=None):
    pass
@frappe.whitelist()
def before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def on_update(doc, method=None):
    pass

import frappe
from frappe.utils import flt

def calculate_additional_discount(doc):
    # Reset discounts
    for row in doc.items:
        row.custom_discount__on_price_list_rate_with_margin = 0
        row.custom_discount_amount = 0

    # Collect pricing rule names
    pricing_rule_names = [row.pricing_rule for row in doc.pricing_rules if row.pricing_rule]

    if not pricing_rule_names:
        return

    # Fetch pricing rule details
    format_strings = ','.join(['%s'] * len(pricing_rule_names))
    details = frappe.db.sql(f"""
        SELECT 
            name,
            custom_pricing_rule_type AS type,
            rate_or_discount,
            discount_percentage,
            discount_amount
        FROM `tabPricing Rule`
        WHERE name IN ({format_strings})
    """, tuple(pricing_rule_names), as_dict=True)

    pricing_rules_dict = {row.name: row for row in details}

    # Initialize accumulators
    shipping_percentage_dict = {}
    default_percentage_dict = {}
    cash_percentage_dict = {}
    shipping_amount_dict = {}
    default_amount_dict = {}
    cash_amount_dict = {}

    # Process each pricing rule
    for row in doc.pricing_rules:
        pricing_rule_name = row.get('pricing_rule')
        item_code = row.get('item_code')
        rule_type = row.get('custom_pricing_rule_type')

        if not pricing_rule_name or not item_code:
            continue

        # Initialize defaults if not present
        shipping_percentage_dict.setdefault(item_code, 0)
        shipping_amount_dict.setdefault(item_code, 0)
        default_percentage_dict.setdefault(item_code, 0)
        default_amount_dict.setdefault(item_code, 0)
        cash_percentage_dict.setdefault(item_code, 0)
        cash_amount_dict.setdefault(item_code, 0)

        rule = pricing_rules_dict.get(pricing_rule_name)
        if not rule:
            continue

        # Accumulate based on type and discount method
        if rule.rate_or_discount == 'Discount Percentage':
            if rule_type == 'Shipping':
                shipping_percentage_dict[item_code] += flt(rule.discount_percentage)
            elif rule_type == 'Default':
                default_percentage_dict[item_code] += flt(rule.discount_percentage)
            elif rule_type == 'Cash':
                cash_percentage_dict[item_code] += flt(rule.discount_percentage)
        elif rule.rate_or_discount == 'Discount Amount':
            if rule_type == 'Shipping':
                shipping_amount_dict[item_code] += flt(rule.discount_amount)
            elif rule_type == 'Default':
                default_amount_dict[item_code] += flt(rule.discount_amount)
            elif rule_type == 'Cash':
                cash_amount_dict[item_code] += flt(rule.discount_amount)

    # Apply calculated discounts to items
    for row in doc.items:
        item_code = row.get('item_code')
        base_amount = flt(row.get('price_list_rate'))
        qty = flt(row.get('qty'))

        # Shipping discount
        shipping_discount = (base_amount * shipping_percentage_dict.get(item_code, 0) / 100) + shipping_amount_dict.get(item_code, 0)
        row.custom_shipping_discount = min(shipping_discount, base_amount) if row.get('custom_apply_shipping_discount') else 0
        row.custom_shipping_ = (row.custom_shipping_discount / base_amount * 100) if base_amount and row.get('custom_apply_shipping_discount') else 0

        # Cash discount
        cash_discount = (base_amount * cash_percentage_dict.get(item_code, 0) / 100) + cash_amount_dict.get(item_code, 0)
        row.custom_cash_discount = min(cash_discount, base_amount) if row.get('custom_apply_cash_discount') else 0
        row.custom_cash_ = (row.custom_cash_discount / base_amount * 100) if base_amount and row.get('custom_apply_cash_discount') else 0

        # Default discount
        default_discount = (base_amount * default_percentage_dict.get(item_code, 0) / 100) + default_amount_dict.get(item_code, 0)
        row.custom_discount_amount = min(default_discount, base_amount)
        row.custom_discount__on_price_list_rate_with_margin = (row.custom_discount_amount / base_amount * 100) if base_amount else 0

        # Final calculated fields
        row.discount_amount = row.custom_shipping_discount + row.custom_cash_discount + row.custom_discount_amount
        row.discount_percentage = row.custom_shipping_ + row.custom_cash_ + row.custom_discount__on_price_list_rate_with_margin

        row.rate = base_amount - row.discount_amount
        row.net_rate = row.rate
        row.base_net_rate = row.rate
        row.base_rate = row.rate

        row.amount = row.rate * qty
        row.base_amount = row.amount
        row.net_amount = row.amount
        row.base_net_amount = row.amount
