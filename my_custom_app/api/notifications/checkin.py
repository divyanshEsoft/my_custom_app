from my_custom_app.api.firebase_utils import notify_employee

def notify(doc, method):
    # Built-in ERPNext Employee Checkin
    action = "Check-in" if doc.log_type == "IN" else "Check-out"

    notify_employee(
        employee=doc.employee,
        title=f"{action} Successful",
        body=f"{action} recorded at {doc.time}",
        data={
            "type": "checkin",
            "log_type": doc.log_type,
            "time": str(doc.time)
        }
    )
