frappe.ui.form.on("Customer", {
    onload: function(frm){
        frm.set_query("territory", { is_group: 1 });
        frm.set_query("route", function(){
            return{
                filters: [
                    ["Territory", "parent_territory", "=", frm.doc.territory]
                ]
            }
        });
    }
})