from __future__ import unicode_literals
import frappe
from frappe import _, bold
from frappe.utils import flt, get_link_to_form

from erpnext.accounts.doctype.pricing_rule.utils import (
    apply_pricing_rule_for_free_items,
    get_applied_pricing_rules,
)
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
    # calculate_additional_discount(doc)
@frappe.whitelist()
def validate(doc, method=None):
    custom_total_amount = 0.0
    for row in doc.items:
        price_list_rate = row.get('price_list_rate') or 0.0
        qty = row.get('qty') or 0.0
        custom_total_amount += price_list_rate * qty
        
    doc.custom_total_amount = custom_total_amount
    
    total = 0
    for row in doc.items:
        total += (row.get('discount_amount', 0) * row.get('qty', 0)) # Correct accumulation
    doc.custom_total_discount = total
    # if doc.custom_mobile == 1 and doc.get("items"):
    #     for item in doc.items:
    #         item_code = item.get("item_code")
    #         if not item_code:
    #             continue

    #         # Fetch Pricing Rule names linked to this item_code via Pricing Rule Item Code child table
    #         pricing_rule_names = frappe.db.get_all(
    #             "Pricing Rule Item Code",
    #             filters={"item_code": item_code},
    #             fields=["parent"]
    #         )
    #         # Extract just the parent names (Pricing Rule names)
    #         pricing_rule_names = [row.parent for row in pricing_rule_names]

    #         # Optionally filter pricing rules that are enabled and selling=1
    #         if pricing_rule_names:
    #             valid_pricing_rules = frappe.db.get_all(
    #                 "Pricing Rule",
    #                 filters={
    #                     "name": ["in", pricing_rule_names],
    #                     # "enabled": 1,
    #                     "selling": 1
    #                 },
    #                 pluck="name"
    #             )
    #         else:
    #             valid_pricing_rules = []

    #         args = {
    #             "pricing_rules": valid_pricing_rules,  # List of applicable Pricing Rule names for this item
    #             "price_list_rate": item.price_list_rate,
    #             "price_or_product_discount": "Price",
    #         }
    #         apply_pricing_rule_on_items(doc, item, args)
    #         set_pricing_rule_details(doc, item, args)
    calculate_tax_per_unit(doc)
    
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

def calculate_additional_discount(doc):
    for row in doc.items:
        price_list_rate = row.get('price_list_rate', 0) or 0
        rate = row.get('rate', 0) or 0
        if rate < price_list_rate and price_list_rate > 0:
            row.custom_discount__on_price_list_rate_with_margin = (((price_list_rate - rate) / price_list_rate) * 100) - (row.get('custom_shipping_', 0) or 0) - (row.get('custom_cash_', 0) or 0)
            row.discount_percentage = ((price_list_rate - rate) / price_list_rate) * 100
            row.custom_discount_amount = (price_list_rate - rate)  - (row.get('custom_shipping_discount', 0) or 0) - (row.get('custom_cash_discount', 0) or 0)
            row.discount_amount = price_list_rate - rate
            
    if doc.ignore_pricing_rule:
        return
        
    for row in doc.items:
        row.custom_discount__on_price_list_rate_with_margin = 0
        row.custom_discount_amount = 0
        custom_tax_amount = row.get('custom_tax_amount') or 0.0
        custom_tax_amount_14_ = row.get('custom_tax_amount_14_') or 0.0
        qty = row.get('qty', 1)
        # frappe.throw(f"rate {row.rate} custom_tax_amount {custom_tax_amount} custom_tax_amount_14_ {custom_tax_amount_14_} ")
        # row.custom_rate_after_tax = row.rate + (custom_tax_amount /  qty) + ( custom_tax_amount_14_ / qty)
        # row.custom_amount_after_tax = row.custom_rate_after_tax * row.get('qty', 0)

    # Get all pricing rule names that are not empty
    pricing_rule_names = list(filter(None, [getattr(row, "pricing_rule", None) for row in doc.pricing_rules]))

    # Fetch pricing rule details safely
    details = []
    if pricing_rule_names:
        details = frappe.get_all(
            "Pricing Rule",
            filters={"name": ["in", pricing_rule_names]},
            fields=[
                "name",
                "custom_pricing_rule_type as type",
                "rate_or_discount",
                "discount_percentage",
                "discount_amount"
            ]
        )

    # Build a dictionary for quick lookup
    pricing_rules_dict = {row["name"]: row for row in details}

    # Initialize accumulators for each discount type by item
    shipping_percentage_dict = {}
    default_percentage_dict = {}
    cash_percentage_dict = {}
    shipping_amount_dict = {}
    default_amount_dict = {}
    cash_amount_dict = {}

    for row in doc.pricing_rules:
        item_code = row.get('item_code')

        # Initialize defaults
        shipping_percentage_dict.setdefault(item_code, 0)
        shipping_amount_dict.setdefault(item_code, 0)
        default_percentage_dict.setdefault(item_code, 0)
        default_amount_dict.setdefault(item_code, 0)
        cash_percentage_dict.setdefault(item_code, 0)
        cash_amount_dict.setdefault(item_code, 0)

    for row in doc.pricing_rules:
        pricing_rule_name = row.get('pricing_rule')
        item_code = row.get('item_code')
        rule = pricing_rules_dict.get(pricing_rule_name)

        if not pricing_rule_name or not item_code or not rule:
            continue

        rule_type = rule.get('type')

        # Classify and accumulate based on type and discount method
        if rule["rate_or_discount"] == 'Discount Percentage':
            if rule_type == 'Shipping':
                shipping_percentage_dict[item_code] += rule.get("discount_percentage", 0)
            elif rule_type == 'Default':
                default_percentage_dict[item_code] += rule.get("discount_percentage", 0)
            elif rule_type == 'Cash':
                cash_percentage_dict[item_code] += rule.get("discount_percentage", 0)
        elif rule["rate_or_discount"] == 'Discount Amount':
            if rule_type == 'Shipping':
                shipping_amount_dict[item_code] += rule.get("discount_amount", 0)
            elif rule_type == 'Default':
                default_amount_dict[item_code] += rule.get("discount_amount", 0)
            elif rule_type == 'Cash':
                cash_amount_dict[item_code] += rule.get("discount_amount", 0)

    # Apply calculated discount values to items
    for row in doc.items:
        item_code = row.get('item_code')
        base_amount = row.get('price_list_rate') or 0

        # Shipping
        shipping_discount = (base_amount * shipping_percentage_dict.get(item_code, 0) / 100) + shipping_amount_dict.get(item_code, 0)
        # Default
        default_discount = (base_amount * default_percentage_dict.get(item_code, 0) / 100) + default_amount_dict.get(item_code, 0)
        # Cash
        cash_discount = (base_amount * cash_percentage_dict.get(item_code, 0) / 100) + cash_amount_dict.get(item_code, 0)

        row.custom_shipping_discount = min(shipping_discount, row.price_list_rate) if row.custom_apply_shipping_discount else 0
        if base_amount != 0:
            row.custom_shipping_ = (row.custom_shipping_discount / base_amount) * 100 if row.custom_apply_shipping_discount else 0
        row.custom_cash_discount = min(cash_discount, row.price_list_rate) if row.custom_apply_cash_discount else 0
        if base_amount != 0:
            row.custom_cash_ = (row.custom_cash_discount / base_amount) * 100 if row.custom_apply_cash_discount else 0

        row.custom_discount_amount = min(default_discount, row.price_list_rate)
        if base_amount != 0:
            row.custom_discount__on_price_list_rate_with_margin = (row.custom_discount_amount / base_amount) * 100

        custom_shipping_discount  = row.get("custom_shipping_discount") or 0.0
        custom_cash_discount = row.get("custom_cash_discount") or 0.0
        custom_discount_amount = row.get("custom_discount_amount") or 0.0
        
        custom_shipping_ = row.get("custom_shipping_") or 0.0
        custom_cash_ = row.get("custom_cash_") or 0.0
        custom_discount__on_price_list_rate_with_margin = row.get("custom_discount__on_price_list_rate_with_margin") or 0.0
        
        row.discount_amount = custom_shipping_discount + custom_cash_discount + custom_discount_amount
        
        row.discount_percentage = custom_shipping_ + custom_cash_ + custom_discount__on_price_list_rate_with_margin

        # row.rate = (row.price_list_rate or 0) - (row.discount_amount or 0)
        # row.net_rate = row.rate
        # row.base_net_rate = row.rate
        # row.base_rate = row.rate
        
        
        custom_tax_amount = row.get('custom_tax_amount') or 0.0
        custom_tax_amount_14_ = row.get('custom_tax_amount_14_') or 0.0
        qty = row.get('qty', 1)
        
        row.item_tax_ = custom_tax_amount + custom_tax_amount_14_

def calaculate_item_taxes(template,amount,qty):
    total_tax_per_unit = 0.0
    tax_rates = frappe.get_all("Item Tax Template Detail", {"parent":template}, pluck = "tax_rate")
    for rate in tax_rates:
        tax_amount = ( (amount * rate) / 100 ) / qty
        total_tax_per_unit += tax_amount
    return total_tax_per_unit
    
def calculate_tax_per_unit(doc):
    if doc.items:
        for row in doc.items:  
            if not row.custom_consumer_rate:
                row.custom_item_tax_for_unit = calaculate_item_taxes(row.item_tax_template,row.amount,row.qty)
            else:
                custom_tax_amount = row.get('custom_tax_amount') or 0.0
                custom_tax_amount_14_ = row.get('custom_tax_amount_14_') or 0.0
                
                custom_item_tax_for_unit = (custom_tax_amount /  row.get('qty', 1)) + (custom_tax_amount_14_ /  row.get('qty', 1))
        
                row.custom_item_tax_for_unit = custom_item_tax_for_unit
                
            row.custom_rate_after_tax = row.get('rate', 0) + row.custom_item_tax_for_unit
            row.custom_amount_after_tax = row.custom_rate_after_tax * row.qty

def apply_pricing_rule_on_items(self, item, pricing_rule_args):
    if not item.get('price_list_rate'):
        return

    raw = pricing_rule_args.get('pricing_rules')

    # Parse pricing rules JSON if string
    if isinstance(raw, str):
        try:
            pricing_rules = json.loads(raw)
        except json.JSONDecodeError:
            pricing_rules = []
    else:
        pricing_rules = raw or []

    # frappe.msgprint(f"Pricing Rules Raw Input: {raw}")

    # Build dicts to identify items eligible for shipping/cash discounts
    shipping_dict = {row.get('item_code'): 1 for row in self.get('items', []) if row.custom_apply_shipping_discount}
    cash_dict = {row.get('item_code'): 1 for row in self.get('items', []) if row.custom_apply_cash_discount}

    total_discount_percentage = 0
    total_discount_amount = 0

    # Fetch pricing rule details once for each pricing rule
    for price_rule_name in pricing_rules:
        price_rule_detail = frappe.db.get_value(
            "Pricing Rule",
            price_rule_name,
            ["custom_pricing_rule_type", "rate_or_discount", "discount_percentage", "discount_amount"],
            as_dict=True,
        )
        if not price_rule_detail:
            continue

        rule_type = price_rule_detail.get('custom_pricing_rule_type')
        rate_or_discount = price_rule_detail.get('rate_or_discount')

        # Check if this rule applies based on type and item eligibility
        applies = (
            rule_type == 'Default' or
            (rule_type == 'Shipping' and item.item_code in shipping_dict) or
            (rule_type == 'Cash' and item.item_code in cash_dict)
        )
        if not applies:
            continue

        # Accumulate discounts
        if rate_or_discount == 'Discount Percentage':
            total_discount_percentage += price_rule_detail.get('discount_percentage', 0)
        else:
            total_discount_amount += price_rule_detail.get('discount_amount', 0)

    price_list_rate = item.get('price_list_rate') or 0
    # Combine discounts into percentage and amount forms (adjusting both ways)
    combined_discount_percentage = total_discount_percentage + (total_discount_amount / price_list_rate * 100 if price_list_rate else 0)
    combined_discount_amount = total_discount_amount + (total_discount_percentage * price_list_rate / 100)

    pricing_rule_args['discount_percentage'] = combined_discount_percentage
    pricing_rule_args['discount_amount'] = combined_discount_amount

    # Apply discounts to the item if validation is not requested
    if not pricing_rule_args.get("validate_applied_rule", 0):
        if pricing_rule_args.get("price_or_product_discount") == "Price":

            # Convert pricing_rules list to comma-separated string for storage
            rules = pricing_rule_args.get("pricing_rules")
            if isinstance(rules, list):
                item.set("pricing_rules", ",".join(rules))
            else:
                item.set("pricing_rules", rules)

            # Optional: restrict application to certain other items
            if pricing_rule_args.get("apply_rule_on_other_items"):
                other_items = json.loads(pricing_rule_args.get("apply_rule_on_other_items"))
                if other_items and item.item_code not in other_items:
                    return

            # Set discount fields on the item row
            item.set("discount_percentage", combined_discount_percentage)
            item.set("discount_amount", combined_discount_amount)

            # Override price_list_rate if needed
            if pricing_rule_args.get("pricing_rule_for") == "Rate":
                item.set("price_list_rate", pricing_rule_args.get("price_list_rate"))

            # Calculate final rate after discounts
            if item.get("price_list_rate"):
                if item.get("discount_amount"):
                    item.rate = flt(item.price_list_rate - item.discount_amount, item.precision("rate"))
                else:
                    item.rate = flt(
                        item.price_list_rate * (1.0 - (flt(item.discount_percentage) / 100.0)),
                        item.precision("rate"),
                    )

            # Override rate if 'apply_discount_on_discounted_rate' and rate provided
            if item.get("apply_discount_on_discounted_rate") and pricing_rule_args.get("rate"):
                item.rate = pricing_rule_args.get("rate")
        
        elif pricing_rule_args.get("free_item_data"):
            # Assuming you have a method for free items
            apply_pricing_rule_for_free_items(self, pricing_rule_args.get("free_item_data"))

    # Validation mode: check if applied discounts are not less than rule discounts
    elif pricing_rule_args.get("validate_applied_rule"):
        for pricing_rule in get_applied_pricing_rules(item.get("pricing_rules")):
            pricing_rule_doc = frappe.get_cached_doc("Pricing Rule", pricing_rule)
            for field in ["discount_percentage", "discount_amount", "rate"]:
                if item.get(field) < pricing_rule_doc.get(field):
                    title = frappe.get_link_to_form("Pricing Rule", pricing_rule)
                    frappe.msgprint(
                        _("Row {0}: user has not applied the rule {1} on the item {2}").format(
                            item.idx, frappe.bold(title), frappe.bold(item.item_code)
                        )
                    )

import json

def set_pricing_rule_details(self, item_row, args):
    raw_pricing_rules = args.get("pricing_rules")
    # Convert list to JSON string before passing to get_applied_pricing_rules
    if isinstance(raw_pricing_rules, list):
        pricing_rules_str = json.dumps(raw_pricing_rules)
    else:
        pricing_rules_str = raw_pricing_rules

    pricing_rules = get_applied_pricing_rules(pricing_rules_str)
    
    if not pricing_rules:
        return

    shipping_dict, cash_dict = {}, {}
    for row in self.get('items', []):
        if row.custom_apply_shipping_discount:
            # frappe.msgprint(str("hello"))
            shipping_dict[row.get('item_code')] = 1
        if row.custom_apply_cash_discount:
            cash_dict[row.get('item_code')] = 1

    for pricing_rule in pricing_rules:
        pricing_rule_type = frappe.get_value("Pricing Rule", pricing_rule, "custom_pricing_rule_type")

        if pricing_rule_type == "Shipping" and item_row.item_code not in shipping_dict:
            continue
        if pricing_rule_type == "Cash" and item_row.item_code not in cash_dict:
            continue

        self.append(
            "pricing_rules",
            {
                "pricing_rule": pricing_rule,
                "item_code": item_row.item_code,
                "child_docname": item_row.name,
                "rule_applied": True,
                "custom_pricing_rule_type": pricing_rule_type,
            },
        )
