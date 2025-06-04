import frappe
import json

from frappe import _, bold
from frappe.utils import flt, get_link_to_form

from erpnext.accounts.doctype.pricing_rule.utils import (
    apply_pricing_rule_for_free_items,
    get_applied_pricing_rules,
)

from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomSalesOrder(SalesOrder):
    def apply_pricing_rule_on_items(self, item, pricing_rule_args):
        # If the item has no base price_list_rate, skip
        if not item.get("price_list_rate"):
            return

        # Load pricing_rules from args (it may be JSON‐encoded string or a list)
        raw = pricing_rule_args.get("pricing_rules")
        if isinstance(raw, str):
            try:
                pricing_rules = json.loads(raw)
            except json.JSONDecodeError:
                pricing_rules = []
        else:
            pricing_rules = raw or []

        # Start discounts at zero for THIS row
        total_discount_percentage = 0
        total_discount_amount = 0

        # Loop through each pricing rule name
        for rule_name in pricing_rules:
            # Fetch type / discount fields from the Pricing Rule doc
            price_rule_detail = frappe.db.sql(
                """
                SELECT 
                    custom_pricing_rule_type AS type,
                    rate_or_discount,
                    discount_percentage,
                    discount_amount
                FROM `tabPricing Rule`
                WHERE name = %s
                """,
                (rule_name,),
                as_dict=True,
            )

            # If the rule doesn’t exist or isn’t found, skip it
            if not price_rule_detail:
                continue

            price_rule_detail = price_rule_detail[0]
            rule_type = price_rule_detail.get("type")
            rod = price_rule_detail.get("rate_or_discount")

            # 1) DEFAULT rules always apply to every row
            if rule_type == "Default":
                if rod == "Discount Percentage":
                    total_discount_percentage += price_rule_detail.get("discount_percentage", 0)
                else:
                    total_discount_amount += price_rule_detail.get("discount_amount", 0)

            # 2) SHIPPING rules apply ONLY if THIS row has custom_apply_shipping_discount = 1
            if rule_type == "Shipping" and item.custom_apply_shipping_discount:
                if rod == "Discount Percentage":
                    total_discount_percentage += price_rule_detail.get("discount_percentage", 0)
                else:
                    total_discount_amount += price_rule_detail.get("discount_amount", 0)

            # 3) CASH rules apply ONLY if THIS row has custom_apply_cash_discount = 1
            if rule_type == "Cash" and item.custom_apply_cash_discount:
                if rod == "Discount Percentage":
                    total_discount_percentage += price_rule_detail.get("discount_percentage", 0)
                else:
                    total_discount_amount += price_rule_detail.get("discount_amount", 0)

        # Now set the new discount fields back onto this row
        price_list_rate = item.get("price_list_rate")
        discount_percentage = total_discount_percentage + (total_discount_amount / price_list_rate * 100)
        total_discount_amount = (discount_percentage * price_list_rate) / 100

        pricing_rule_args["discount_percentage"] = discount_percentage
        pricing_rule_args["discount_amount"] = total_discount_amount
        
        # If validate_applied_rule is false (i.e. we are actually applying, not just validating)
        if not pricing_rule_args.get("validate_applied_rule", 0):
            # If the user is applying a price‐based discount...
            if pricing_rule_args.get("price_or_product_discount") == "Price":
                # (Re‐set the “pricing_rules” field, in case they changed it manually)
                item.set("pricing_rules", pricing_rule_args.get("pricing_rules"))

                # If there’s an “apply_rule_on_other_items” list, make sure this row is in that list
                if pricing_rule_args.get("apply_rule_on_other_items"):
                    other_items = json.loads(pricing_rule_args.get("apply_rule_on_other_items"))
                    if other_items and item.item_code not in other_items:
                        return

                # Push the calculated discounts onto the row
                item.set("discount_percentage", pricing_rule_args["discount_percentage"])
                item.set("discount_amount", pricing_rule_args["discount_amount"])
                if pricing_rule_args.get("pricing_rule_for") == "Rate":
                    # If you’re overriding the base rate, set it now
                    item.set("price_list_rate", pricing_rule_args.get("price_list_rate"))

                # Recalculate “rate” based on discount %
                if price_list_rate:
                    # Percentage‐based rate
                    item.rate = flt(
                        price_list_rate * (1.0 - (flt(total_discount_percentage) / 100.0)),
                        item.precision("rate"),
                    )

                    # If there’s also a flat discount_amount, subtract that too
                    if total_discount_amount:
                        item.rate = price_list_rate - total_discount_amount

                # If “apply discount on discounted rate” is set, take that override
                if item.get("apply_discount_on_discounted_rate") and pricing_rule_args.get("rate"):
                    item.rate = pricing_rule_args.get("rate")

            # If it’s a “free item” rule
            elif pricing_rule_args.get("free_item_data"):
                apply_pricing_rule_for_free_items(self, pricing_rule_args.get("free_item_data"))

        # If we’re only validating (“validate_applied_rule = 1”), check that the row’s discounts aren’t less
        # than the minimums on any applied Pricing Rule
        elif pricing_rule_args.get("validate_applied_rule"):
            for applied_rule in get_applied_pricing_rules(item.get("pricing_rules")):
                pricing_rule_doc = frappe.get_cached_doc("Pricing Rule", applied_rule)
                for fld in ["discount_percentage", "discount_amount", "rate"]:
                    if item.get(fld) < pricing_rule_doc.get(fld):
                        title = get_link_to_form("Pricing Rule", applied_rule)
                        frappe.msgprint(
                            _("Row {0}: user has not applied the rule {1} on the item {2}").format(
                                item.idx, bold(title), bold(item.item_code)
                            )
                        )

    def set_pricing_rule_details(self, item_row, args):
        pricing_rules = get_applied_pricing_rules(args.get("pricing_rules"))
        if not pricing_rules:
            return

        shipping_dict, cash_dict = {}, {}
        for row in self.get('items', []):
            if row.custom_apply_shipping_discount:
                shipping_dict[row.name] = True
            if row.custom_apply_cash_discount:
                cash_dict[row.name] = True

        for pricing_rule in pricing_rules:
            pricing_rule_type = frappe.get_value("Pricing Rule", pricing_rule, "custom_pricing_rule_type")

            if pricing_rule_type == "Shipping" and item_row.name not in shipping_dict:
                continue
            if pricing_rule_type == "Cash" and item_row.name not in cash_dict:
                continue

            if not self.get("pricing_rules", {
                "pricing_rule": pricing_rule,
                "item_code": item_row.item_code,
            }):
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