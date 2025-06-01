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