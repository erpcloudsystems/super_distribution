frappe.ui.form.on("Purchase Order Item", {
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