import frappe
from frappe import _

@frappe.whitelist()
def get_total_leave_requests(employee: str, month: str, year: str):
        """
        Get total leave requests for an employee in a given month and year.
        
        Args:
            employee (str): Employee ID (e.g., "EMP-0001")
            month (str): Month number (e.g., "08")
            year (str): Year (e.g., "2025")
        
        Returns:
            dict: Total leave requests
        """
        try:
            start_date = f"{year}-{month}-01"
            # frappe automatically handles end_of_month via dateutil
            end_date = frappe.utils.get_last_day(start_date)

            total_requests = frappe.db.count(
                "Leave Application",
                filters={
                    "employee": employee,
                    "from_date": [">=", start_date],
                    "from_date": ["<=", end_date],
                },
            )

            return {"employee": employee, "month": month, "year": year, "total_leave_requests": total_requests}

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Leave Request Count API Error")
            return {"error": str(e)}
