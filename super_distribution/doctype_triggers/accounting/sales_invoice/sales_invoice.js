frappe.ui.form.on("Sales Invoice", {
    customer: function(frm){
        if(frm.doc.customer){
            frappe.db.get_doc("Customer", frm.doc.customer
            ).then(res => {
                if (res) {
                    if (res.sales_team.length) {
                        frm.set_value("sales_person", res.sales_team[0].sales_person);
                    }
                    if (res.credit_limits.length) {
                        frm.set_value("customer_credit_limit", res.credit_limits[0].credit_limit);
                    }
                }
            });
        }
        else {
            frm.set_value("sales_person", "");
            frm.set_value("customer_credit_limit", "");
        }
    }
});

frappe.ui.form.on("Sales Invoice", {
    custom_cash: function(frm) {
        apply_cash_discount_to_all_items(frm);
    },
    custom_type: function(frm) {
        apply_shipping_discount_to_all_items(frm);
    },
});

frappe.ui.form.on("Sales Invoice Item", {
    item_code: function(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        row.custom_apply_cash_discount = frm.doc.custom_cash;
        row.custom_apply_shipping_discount = (frm.doc.custom_type == 'سيارات العميل');
        frm.refresh_field('items');
    },
});

function apply_cash_discount_to_all_items(frm) {
    frm.doc.items.forEach(row => {
        row.custom_apply_cash_discount = frm.doc.custom_cash;
    });
    frm.refresh_field('items');
}

function apply_shipping_discount_to_all_items(frm) {
    frm.doc.items.forEach(row => {
        row.custom_apply_shipping_discount = (frm.doc.custom_type == 'سيارات العميل');
    });
    frm.refresh_field('items');
}

frappe.ui.form.on('Sales Invoice Item', {
    rate: function(frm, cdt, cdn) {
        let item = locals[cdt][cdn];
        if (frm.doc.ignore_pricing_rule && item.price_list_rate > 0) {
            let discount = ((item.price_list_rate - item.rate) / item.price_list_rate) * 100;
            frappe.model.set_value(cdt, cdn, "discount_percentage", discount);
        }
    }
});

frappe.ui.form.on('Sales Invoice', {
    before_save: function(frm) {
        frm.doc.items.forEach(item => {
            if (frm.doc.ignore_pricing_rule && item.price_list_rate && item.rate !== item.price_list_rate) {
                let discount = ((item.price_list_rate - item.rate) / item.price_list_rate) * 100;
                item.discount_percentage = discount;
            }
        });
        frm.refresh_field("items");
    }
});
