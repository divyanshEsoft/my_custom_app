import frappe


@frappe.whitelist()
def deactivate_device(device_id):
    frappe.db.sql("""
        UPDATE `tabEmployee Device`
        SET is_active = 0
        WHERE device_id = %s
    """, device_id)

    frappe.db.commit()
