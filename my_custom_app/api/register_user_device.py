
import frappe

@frappe.whitelist()
def register_device(employee, device_id, fcm_token, platform=None):
    frappe.logger().info(
        f"FCM: Register device | emp={employee} | device={device_id}"
    )

    # deactivate old tokens for same device
    frappe.db.sql("""
        UPDATE `tabEmployee Device`
        SET is_active = 0
        WHERE employee = %s AND device_id = %s
    """, (employee, device_id))

    # check if token already exists
    existing = frappe.db.get_value(
        "Employee Device",
        {"fcm_token": fcm_token},
        "name"
    )

    if existing:
        doc = frappe.get_doc("Employee Device", existing)
        doc.is_active = 1
        doc.employee = employee
        doc.device_id = device_id
        doc.platform = platform
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({
            "doctype": "Employee Device",
            "employee": employee,
            "device_id": device_id,
            "fcm_token": fcm_token,
            "platform": platform,
            "is_active": 1
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return {"status": "ok"}





# # erpnext_mobile_notify/api.py
# import frappe

# @frappe.whitelist(allow_guest=True)
# def register_device(employee, device_id, fcm_token, platform=None):
#     """
#     Register or update employee device for push notifications.
#     Handles:
#       - Same employee + device_id → update token
#       - Same employee + new device_id → create new device row
#       - Different employee + same device_id → reassign device
#     """


#     # Case 1 or 3: Check if device_id already exists
#     existing = frappe.get_all(
#         "Employee Device",
#         filters={"device_id": device_id},
#         fields=["name", "employee"]
#     )

#     if existing:
#         doc = frappe.get_doc("Employee Device", existing[0].name)
#         # If device already linked to another employee → reassign
#         if doc.employee != employee:
#             doc.employee = employee
#         doc.fcm_token = fcm_token
#         if platform:
#             doc.platform = platform
#         doc.save(ignore_permissions=True)
#         status = "updated/reassigned"
#     else:
#         # Case 2: new device for employee
#         doc = frappe.get_doc({
#             "doctype": "Employee Device",
#             "employee": employee,
#             "device_id": device_id,
#             "fcm_token": fcm_token,
#             "platform": platform
#         })
#         doc.insert(ignore_permissions=True)
#         status = "created"

#     frappe.db.commit()
#     return {
#         "status": status,
#         "device_id": device_id,
#         "employee": employee,
#         "fcm_token": fcm_token
#     }

