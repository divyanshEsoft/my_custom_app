import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def get_total_attendance_counts(employee , from_date=None , to_date=None):
     """
    Get attendance counts for an employee.
    Present-like = Present (1) + Half Day (0.5) + Work From Home (1)
    Absent = Absent + on Leave
    
    Optionally filter by date range.
    """
     try:
          filters = {"employee" :employee}

          if from_date and to_date:
               filters["attendance_date"] = ["between", [from_date, to_date]]

    # Count Present-like statuses
          present_count = frappe.db.count("Attendance", {**filters, "status": "Present"})
          half_day_count = frappe.db.count("Attendance", {**filters, "status": "Half Day"})
          wfh_count = frappe.db.count("Attendance", {**filters, "status": "Work From Home"})

        # Count Absent /Leave
          absent_count = frappe.db.count("Attendance", {**filters, "status": "Absent"})

          leave_count = frappe.db.count("Attendance" , {**filters , "status" : "On Leave"})


          # Calculate combined present-like total
          present_day_count = present_count + (half_day_count * 0.5)+ wfh_count


          #calculate the combined On Leave and Absent total
          absent_day_count = absent_count +leave_count

          return {
               "present_day_count" : present_day_count,
               "absent_count" : absent_day_count
          }
     

     except Exception as e:
          frappe.log_error(message=str(e), title="Attendance Count API Error")
          return {"error": str(e)}
     