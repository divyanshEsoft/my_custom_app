import frappe
from my_custom_app.api.notify_employee import notify_employee

def notify(doc, method):
    frappe.logger().info(
        f"Leave Notify Triggered | Doc={doc.name} | Status={doc.docstatus}"
    )

    if doc.docstatus != 1:
        return

    notify_employee(
        employee=doc.employee,
        title="Leave Approved",
        body=f"Leave from {doc.from_date} to {doc.to_date} approved",
        data={
            "type": "leave",
            "docname": doc.name
        }
    )





# def notify(doc, method):
#     # Only after approval
#     if doc.docstatus != 1:
#         return

#     notify_employee(
#         employee=doc.employee,
#         title="Leave Approved",
#         body=f"Leave from {doc.from_date} to {doc.to_date} approved",
#         data={
#             "type": "leave",
#             "from": str(doc.from_date),
#             "to": str(doc.to_date),
#             "leave_type": doc.leave_type
#         }
#     )
