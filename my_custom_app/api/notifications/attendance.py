from my_custom_app.api.notify_employee import notify_employee

def notify(doc, method):
    if doc.docstatus != 1:
        return

    notify_employee(
        employee=doc.employee,
        title="Attendance Approved",
        body=f"Attendance for {doc.attendance_date} approved",
        data={
            "type": "attendance",
            "date": str(doc.attendance_date),
            "status": doc.status
        }
    )
