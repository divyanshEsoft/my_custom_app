import frappe
from datetime import datetime, timedelta, date
from frappe import _


@frappe.whitelist(allow_guest=False)
def get_full_month_attendance(**kwargs):
    """
    Custom API to return full attendance data for a date range.

    - Returns all dates between from_date and to_date.
    - Fills missing past days as 'Absent' virtual records.
    - Filters out irrelevant fields like naming_series, leave_type, etc.
    - Returns clean, consistent structure for frontend use.
    """
    try:
        # -------------------- PARAMETER VALIDATION --------------------
        employee = kwargs.get("employee")
        from_date = kwargs.get("from_date")
        to_date = kwargs.get("to_date")

        if not all([employee, from_date, to_date]):
            return {"data": [], "error": "Missing required parameters: employee, from_date, to_date"}

        if not frappe.db.exists("Employee", employee):
            return {"data": [], "error": _(f"Employee {employee} does not exist")}

        # -------------------- DATE HANDLING --------------------
        def to_date_obj(val):
            if isinstance(val, (datetime, date)):
                return val.date() if isinstance(val, datetime) else val
            return datetime.strptime(str(val), "%Y-%m-%d").date()

        try:
            start_date = to_date_obj(from_date)
            end_date = to_date_obj(to_date)
        except Exception as e:
            return {"data": [], "error": f"Invalid date format: {str(e)}"}

        today = datetime.now().date()
        if end_date > today:
            end_date = today
        if start_date > today:
            return {"data": []}

        # -------------------- FIELD SELECTION --------------------
        meta = frappe.get_meta("Attendance")
        valid_fields = [
            f.fieldname for f in meta.fields
            if f.fieldtype not in ["Table", "HTML", "Section Break", "Column Break"]
        ]

        # Ensure key fields exist
        for key in ["name", "employee", "attendance_date", "status", "company", "in_time", "out_time", "working_hours", "shift", "late_entry", "early_exit"]:
            if key not in valid_fields:
                valid_fields.append(key)

        # Fetch attendance records
        records = frappe.get_all(
            "Attendance",
            filters={"employee": employee, "attendance_date": [
                "between", [start_date, end_date]]},
            fields=valid_fields,
            order_by="attendance_date desc",
        )

        # -------------------- EMPLOYEE DETAILS --------------------
        emp = frappe.get_doc("Employee", employee)
        emp_name = emp.employee_name
        company = emp.company
        department = getattr(emp, "department", None)

        # -------------------- MAP EXISTING RECORDS --------------------
        existing = {}
        for r in records:
            adate = r.get("attendance_date")
            if isinstance(adate, (datetime, date)):
                adate = adate.strftime("%Y-%m-%d")
            existing[adate] = {
                "name": r.get("name"),
                "employee": r.get("employee"),
                "employee_name": emp_name,
                "attendance_date": adate,
                "status": r.get("status"),
                "company": r.get("company"),
                "department": department,
                "shift": r.get("shift"),
                "in_time": r.get("in_time"),
                "out_time": r.get("out_time"),
                "working_hours": r.get("working_hours"),
                "late_entry": r.get("late_entry"),
                "early_exit": r.get("early_exit"),
                "is_virtual": False,
            }

        # -------------------- BUILD COMPLETE RANGE --------------------
        data = []
        current = start_date
        while current <= end_date:
            cdate = current.strftime("%Y-%m-%d")
            if cdate in existing:
                data.append(existing[cdate])
            elif current < today:
                # Create virtual Absent record
                data.append({
                    "name": f"VIRTUAL-ABSENT-{employee}-{cdate}",
                    "employee": employee,
                    "employee_name": emp_name,
                    "attendance_date": cdate,
                    "status": "Absent",
                    "company": company,
                    "department": department,
                    "shift": None,
                    "in_time": None,
                    "out_time": None,
                    "working_hours": 0.0,
                    "late_entry": 0,
                    "early_exit": 0,
                    "is_virtual": True,
                })
            current += timedelta(days=1)

        # Sort descending by date
        data.sort(key=lambda x: x["attendance_date"], reverse=True)

        return {"data": data}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(),
                         "Full Month Attendance Clean API Error")
        return {"data": [], "error": str(e)}


# import frappe
# from datetime import datetime, timedelta, date
# from frappe import _


# @frappe.whitelist(allow_guest=False)
# def get_full_month_attendance(**kwargs):
#     """
#     Custom API to return full attendance data for a date range.
#     - Returns 'Absent' for missing past dates.
#     - Skips future dates.
#     - Future-proof: handles additional fields dynamically.
#     """
#     try:
#         # -------------------- PARAMETER EXTRACTION --------------------
#         employee = kwargs.get('employee')
#         from_date = kwargs.get('from_date')
#         to_date = kwargs.get('to_date')

#         # Validate required params
#         if not all([employee, from_date, to_date]):
#             return {"data": [], "error": "Missing required parameters: employee, from_date, to_date"}

#         # Validate employee existence
#         if not frappe.db.exists("Employee", employee):
#             return {"data": [], "error": _("Employee {0} does not exist").format(employee)}

#         # -------------------- DATE PARSING --------------------
#         def to_date_obj(value):
#             """Convert incoming values to Python date object."""
#             if isinstance(value, datetime):
#                 return value.date()
#             if isinstance(value, date):
#                 return value
#             return datetime.strptime(str(value), "%Y-%m-%d").date()

#         try:
#             start_date_obj = to_date_obj(from_date)
#             end_date_obj = to_date_obj(to_date)
#         except Exception as e:
#             return {"data": [], "error": f"Invalid date format: {str(e)}"}

#         today = datetime.now().date()
#         if end_date_obj > today:
#             end_date_obj = today
#         if start_date_obj > today:
#             return {"data": []}

#         # Limit to last 1 year
#         one_year_ago = today - timedelta(days=365)
#         if start_date_obj < one_year_ago:
#             start_date_obj = one_year_ago

#         start_date_str = start_date_obj.strftime("%Y-%m-%d")
#         end_date_str = end_date_obj.strftime("%Y-%m-%d")

#         # -------------------- FIELD SELECTION --------------------
#         meta = frappe.get_meta("Attendance")

#         # ✅ Get only valid database columns (skip child tables, UI elements, etc.)
#         fields = [
#             f.fieldname for f in meta.fields
#             if f.fieldtype not in ["Table", "Table MultiSelect", "HTML", "Section Break", "Column Break"]
#         ]

#         # Ensure mandatory fields are always present
#         for mandatory in ["name", "attendance_date", "status", "employee", "company"]:
#             if mandatory not in fields:
#                 fields.insert(0, mandatory)

#         # -------------------- FETCH ATTENDANCE RECORDS --------------------
#         records = frappe.get_all(
#             "Attendance",
#             filters={
#                 "employee": employee,
#                 "attendance_date": ["between", [start_date_str, end_date_str]],
#             },
#             fields=fields,
#             order_by="attendance_date desc",
#         )

#         # Map records by date string (YYYY-MM-DD)
#         attendance_map = {}
#         for r in records:
#             att_date = r.get("attendance_date")
#             if isinstance(att_date, (datetime, date)):
#                 date_str = att_date.strftime("%Y-%m-%d")
#             elif isinstance(att_date, str):
#                 date_str = att_date.split(" ")[0]
#             else:
#                 continue
#             attendance_map[date_str] = r

#         # -------------------- EMPLOYEE INFO --------------------
#         emp_doc = frappe.get_doc("Employee", employee)
#         emp_name = emp_doc.employee_name
#         company = emp_doc.company

#         # -------------------- BUILD RESULT --------------------
#         result = []
#         current_date = start_date_obj
#         while current_date <= end_date_obj:
#             date_str = current_date.strftime("%Y-%m-%d")

#             if date_str in attendance_map:
#                 rec = attendance_map[date_str]
#                 rec.setdefault("employee", employee)
#                 rec.setdefault("employee_name", emp_name)
#                 rec.setdefault("company", company)
#                 result.append(rec)
#             elif current_date < today:
#                 absent_record = {f: None for f in fields}
#                 absent_record.update({
#                     "employee": employee,
#                     "employee_name": emp_name,
#                     "company": company,
#                     "attendance_date": date_str,
#                     "status": "Absent",
#                     "working_hours": 0.0
#                 })
#                 result.append(absent_record)

#             current_date += timedelta(days=1)

#         # -------------------- SORT AND RETURN --------------------
#         result.sort(
#             key=lambda x: datetime.strptime(
#                 str(x.get("attendance_date", "1900-01-01")), "%Y-%m-%d"),
#             reverse=True
#         )

#         return {"data": result}

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(),
#                          "Full Month Attendance History API Error")

#         # During development, show the error message directly:
#         return {"data": [], "error": str(e)}

#         # In production, replace the above line with:
#         # return {"data": [], "error": _("Internal server error. Please contact support.")}
