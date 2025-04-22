frappe.ui.form.on("Sales Order", {
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

frappe.ui.form.on("Sales Order Item", {
	"rate": function (frm, cdt, cdn) {
		set_discount(frm, cdt, cdn);
		set_total_discount(frm);
	},
	"qty": function (frm, cdt, cdn) {
		set_discount(frm, cdt, cdn);
		set_total_discount(frm);
	},
	"shipping_discount": function (frm, cdt, cdn) {
		set_discount(frm, cdt, cdn);
		set_total_discount(frm);
	}
});

function set_discount(frm, cdt, cdn) {
	var row = locals[cdt][cdn];
	if(row.rate && row.rate < row.shipping_discount){
		frappe.throw(__("Rate Can Not Be Lesser Then Shipping Discount <b>{0}.</b>",[row.shipping_discount]));
	}
	else{
		frappe.model.set_value(cdt, cdn, "total_shipping_discount", row.qty * row.shipping_discount);
	}
}

function set_total_discount(frm) {
	var total_discount = 0;
	var items = frm.doc.items;
	for (var i = 0; i < items.length; i++) {
		total_discount += items[i].total_shipping_discount;
	}
    frm.set_value("discount_amount", total_discount);
    frm.refresh_fields();
	
}