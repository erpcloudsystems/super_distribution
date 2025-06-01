import frappe
import json

from frappe import _, bold
from frappe.utils import flt, get_link_to_form

from erpnext.accounts.doctype.pricing_rule.utils import (
    apply_pricing_rule_for_free_items,
    get_applied_pricing_rules,
)

from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote

class CustomDeliveryNote(DeliveryNote):
    def apply_pricing_rule_on_items(self, item, pricing_rule_args):
        if not item.get('price_list_rate'):
            return

        raw = pricing_rule_args.get('pricing_rules')
        
        if isinstance(raw, str):
            try:
                pricing_rules = json.loads(raw)
            except json.JSONDecodeError:
                pricing_rules = []
        else:
            pricing_rules = raw

        shipping_dict, cash_dict = {}, {}
        for row in self.get('items', []):
            if row.custom_apply_shipping_discount:
                shipping_dict[row.get('item_code')] = 1
            if row.custom_apply_cash_discount:
                cash_dict[row.get('item_code')] = 1
        
        total_discount_percentage = 0
        total_discount_amount = 0

        for price_rule in pricing_rules:
            # Fetch pricing rule details from DB
            price_rule_detail = frappe.db.sql("""
                SELECT 
                    custom_pricing_rule_type AS type,
                    rate_or_discount,
                    discount_percentage,
                    discount_amount
                FROM `tabPricing Rule`
                WHERE name = %s
            """, (price_rule,), as_dict=True)

            if not price_rule_detail:
                continue

            price_rule_detail = price_rule_detail[0]

            # Calculate the amount and percentage discount for applicable pricing rule
            if price_rule_detail.get('type') == 'Default':
                if price_rule_detail.get('rate_or_discount') == 'Discount Percentage':
                    total_discount_percentage += price_rule_detail.get('discount_percentage', 0)
                else:
                    total_discount_amount += price_rule_detail.get('discount_amount', 0)
            if price_rule_detail.get('type') == 'Shipping' and item.item_code in shipping_dict:
                if price_rule_detail.get('rate_or_discount') == 'Discount Percentage':
                    total_discount_percentage += price_rule_detail.get('discount_percentage', 0)
                else:
                    total_discount_amount += price_rule_detail.get('discount_amount', 0)
            if price_rule_detail.get('type') == 'Cash' and item.item_code in cash_dict:
                if price_rule_detail.get('rate_or_discount') == 'Discount Percentage':
                    total_discount_percentage += price_rule_detail.get('discount_percentage', 0)
                else:
                    total_discount_amount += price_rule_detail.get('discount_amount', 0)
        
        # Set The New discount_percentage and discount_amount for this Item 
        price_list_rate = item.get('price_list_rate')
        pricing_rule_args['discount_percentage'] = total_discount_percentage # + (total_discount_amount / price_list_rate * 100)
        pricing_rule_args['discount_amount'] =  total_discount_amount # + (total_discount_percentage * price_list_rate / 100)
                
        if not pricing_rule_args.get("validate_applied_rule", 0):
            # if user changed the discount percentage then set user's discount percentage ?
            if pricing_rule_args.get("price_or_product_discount") == "Price":
                item.set("pricing_rules", pricing_rule_args.get("pricing_rules"))
                if pricing_rule_args.get("apply_rule_on_other_items"):
                    other_items = json.loads(pricing_rule_args.get("apply_rule_on_other_items"))
                    if other_items and item.item_code not in other_items:
                        return

                item.set("discount_percentage", pricing_rule_args.get("discount_percentage"))
                item.set("discount_amount", pricing_rule_args.get("discount_amount"))
                if pricing_rule_args.get("pricing_rule_for") == "Rate":
                    item.set("price_list_rate", pricing_rule_args.get("price_list_rate"))

                if item.get("price_list_rate"):
                    item.rate = flt(
                        item.price_list_rate * (1.0 - (flt(item.discount_percentage) / 100.0)),
                        item.precision("rate"),
                    )

                    if item.get("discount_amount"):
                        item.rate = item.price_list_rate - item.discount_amount

                if item.get("apply_discount_on_discounted_rate") and pricing_rule_args.get("rate"):
                    item.rate = pricing_rule_args.get("rate")

            elif pricing_rule_args.get("free_item_data"):
                apply_pricing_rule_for_free_items(self, pricing_rule_args.get("free_item_data"))

        elif pricing_rule_args.get("validate_applied_rule"):
            for pricing_rule in get_applied_pricing_rules(item.get("pricing_rules")):
                pricing_rule_doc = frappe.get_cached_doc("Pricing Rule", pricing_rule)
                for field in ["discount_percentage", "discount_amount", "rate"]:
                    if item.get(field) < pricing_rule_doc.get(field):
                        title = get_link_to_form("Pricing Rule", pricing_rule)

                        frappe.msgprint(
                            _("Row {0}: user has not applied the rule {1} on the item {2}").format(
                                item.idx, frappe.bold(title), frappe.bold(item.item_code)
                            )
                        )
                        
    def set_pricing_rule_details(self, item_row, args):
        pricing_rules = get_applied_pricing_rules(args.get("pricing_rules"))
        if not pricing_rules:
            return

        shipping_dict, cash_dict = {}, {}
        for row in self.get('items', []):
            if row.custom_apply_shipping_discount:
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