import json
import requests
import frappe
from google.oauth2 import service_account
from google.auth.transport.requests import Request

FCM_SCOPE = ["https://www.googleapis.com/auth/firebase.messaging"]

def get_access_token():
    settings = frappe.get_single("Firebase Settings")

    frappe.logger().info("FCM: Reading Firebase Settings")

    if not settings.service_account_json:
        frappe.throw("Firebase service_account_json is empty")

    creds_info = json.loads(settings.service_account_json)

    credentials = service_account.Credentials.from_service_account_info(
        creds_info, scopes=FCM_SCOPE
    )
    credentials.refresh(Request())

    frappe.logger().info(
        f"FCM: Access token generated for project {creds_info.get('project_id')}"
    )

    return credentials.token, creds_info["project_id"]



def send_fcm_notification(token, title, body, data=None):
    frappe.logger().info(
        f"FCM: Sending notification | Token={token[:20]}... | Title={title}"
    )

    access_token, project_id = get_access_token()

    payload = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data or {}
        }
    }

    response = requests.post(
        f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    frappe.logger().info(
        f"FCM Response Status={response.status_code}, Body={response.text}"
    )

    if response.status_code != 200:
        frappe.log_error(
            response.text,
            "FCM Send Error"
        )

    return response.json()
