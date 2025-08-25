import frappe, requests, json
from frappe.utils import format_datetime

def send_push_notification(token, title, body):
    """Send push notification to FCM"""
    server_key = frappe.conf.get("fcm_server_key")
    if not server_key:
        frappe.throw("FCM Server Key not configured in site_config.json")

    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": "key=" + server_key,
        "Content-Type": "application/json"
    }
    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body,
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
    }

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    if res.status_code != 200:
        frappe.log_error(f"FCM Error: {res.text}", "Push Notification Failed")


def send_checkin_notification(doc, method):
    """Called automatically after Employee Checkin insert"""
    try:
        employee = frappe.get_doc("Employee", doc.employee)
        devices = frappe.get_all(
            "Employee Device",
            filters={"employee": employee.name},
            fields=["fcm_token"]
        )

        msg = "Checked {} at {}".format(
            "in" if doc.log_type == "IN" else "out",
            format_datetime(doc.time, "HH:mm")
        )
        #########################################################
        frappe.logger().info(f"Sending push notification for {doc.employee} - {doc.log_type} at {doc.time}")

        for d in devices:
            if d.fcm_token:
                send_push_notification(d.fcm_token, "Attendance Update", msg)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Checkin Notification Error")