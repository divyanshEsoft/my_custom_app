import frappe
from my_custom_app.api.firebase_utils import send_fcm_notification

def notify_employee(employee, title, body, data=None):
    settings = frappe.get_single("Firebase Settings")
    if not settings.enabled:
        return

    tokens = frappe.get_all(
        "Employee Device",
        filters={"employee": employee, "is_active": 1},
        pluck="fcm_token"
    )

    for token in tokens:
        send_fcm_notification(
            token=token,
            title=title,
            body=body,
            data=data or {}
        )








# import frappe
# from my_custom_app.api.firebase_utils import send_fcm_notification

# # def notify_employee(employee, title, body, data=None):

# #     frappe.logger().info(f"FCM: notify_employee called for {employee}")

# #     devices = frappe.get_all(
# #         "Employee Device",
# #         filters = {
            
# #             "employee": employee,
# #             "is_active": 1
# #         },
# #         fields=["name", "fcm_token"]

# #     )

# #     if not devices:
# #         frappe.logger().warning(
# #             f"FCM: No active devices found for employee {employee}"
# #         )
# #         return
    
# #     for d in devices:
# #         frappe.logger().info(
# #             f"FCM: Sending to device {d.name}"
# #         )
# #         send_fcm_notification(
# #             token=d.fcm_token,
# #             title=title,
# #             body=body,
# #             data=data or {}
# #         )



# def notify_employee(employee, title, body, data=None):
#     frappe.logger().info(
#         f"FCM: notify_employee called | employee={employee}"
#     )

#     settings = frappe.get_single("Firebase Settings")
#     if not settings.enabled:
#         frappe.logger().warning("FCM: Firebase disabled in settings")
#         return

#     devices = frappe.get_all(
#         "Employee Device",
#         filters={
#             "employee": employee,
#             "is_active": 1
#         },
#         fields=["name", "fcm_token"]
#     )

#     if not devices:
#         frappe.logger().warning(
#             f"FCM: No active devices found for employee {employee}"
#         )
#         return

#     for d in devices:
#         frappe.logger().info(
#             f"FCM: Sending to device {d.name}"
#         )
#         send_fcm_notification(
#             token=d.fcm_token,
#             title=title,
#             body=body,
#             data=data or {}
#         )
