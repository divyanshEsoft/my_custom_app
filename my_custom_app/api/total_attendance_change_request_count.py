import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def get_attendance_change_request_counts(employee, from_date=None, to_date=None):
    """
    Get total Attendance Change Requests for an employee.
    Optionally filter by date range.
    """
    try:
        filters = {"employee": employee}

        # Date range filter
        if from_date and to_date:
            filters["from_date"] = (">=", from_date)
            filters["to_date"] = ("<=", to_date)

        # Count Attendance Change Requests
        count = frappe.db.count("Attendance Request", filters)

        return {"employee": employee, "count": count}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Attendance Change Request Count Error")
        return {"error": str(e)}