# erpnext/erpnext/human_resources/api/attendance_api.py
import frappe
from frappe import _
from frappe.utils import now_datetime
import json
from .attendance_service import AttendanceService

@frappe.whitelist(allow_guest=False)
def mark_checkin(**kwargs):
    """
    API endpoint for employee check-in
    """
    return _process_attendance_request("IN", **kwargs)

@frappe.whitelist(allow_guest=False)
def mark_checkout(**kwargs):
    """
    API endpoint for employee check-out
    """
    return _process_attendance_request("OUT", **kwargs)

@frappe.whitelist(allow_guest=False)
def mark_attendance(**kwargs):
    """
    Generic API endpoint for attendance marking
    Accepts both IN and OUT
    """
    log_type = kwargs.get('log_type')
    if not log_type:
        return {
            "success": False,
            "error": "log_type parameter is required (IN/OUT)"
        }
    
    return _process_attendance_request(log_type, **kwargs)

def _process_attendance_request(log_type: str, **kwargs):
    """Process attendance request with common validation"""
    try:
        # Get employee from session if not provided
        employee = kwargs.get('employee')
        if not employee and frappe.session.user != "Administrator":
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
        if not employee:
            return {
                "success": False,
                "error": "Employee not specified and cannot be determined from session"
            }
        
        # Parse timestamp if provided
        timestamp = kwargs.get('timestamp')
        if timestamp:
            from frappe.utils import get_datetime
            timestamp = get_datetime(timestamp)
        
        # Initialize service and process
        service = AttendanceService()
        result = service.mark_attendance(
            employee=employee,
            log_type=log_type,
            timestamp=timestamp,
            shift=kwargs.get('shift'),
            ip_address=frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None,
            device_id=kwargs.get('device_id'),
            location=kwargs.get('location')
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Attendance API Request Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=False)
def get_attendance_status(employee: str = None, date: str = None):
    """
    Get attendance status for an employee on a specific date
    """
    try:
        if not employee and frappe.session.user != "Administrator":
            employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        
        if not employee:
            return {"success": False, "error": "Employee not specified"}
        
        from frappe.utils import getdate, nowdate
        if not date:
            date = nowdate()
        
        attendance = frappe.db.get_value("Attendance", {
            "employee": employee,
            "attendance_date": getdate(date),
            "docstatus": 1
        }, ["name", "status", "in_time", "out_time", "shift"], as_dict=True)
        
        return {
            "success": True,
            "attendance": attendance,
            "date": date
        }
        
    except Exception as e:
        frappe.log_error(f"Attendance Status API Error: {str(e)}")
        return {"success": False, "error": str(e)}