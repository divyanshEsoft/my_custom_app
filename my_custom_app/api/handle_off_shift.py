
# import frappe
# from frappe.utils import get_datetime
# from erpnext.hr.doctype.shift_assignment.shift_assignment import get_actual_start_end_datetime_of_shift

# def mark_attendance_with_off_shift(doc, method):
#     employee = doc.employee
#     checkin_time = get_datetime(doc.time)

#     # Fetch all active shifts for the date
#     shifts = frappe.get_all("Shift Assignment",
#         filters={
#             "employee": employee,
#             "start_date": ["<=", checkin_time.date()],
#             "end_date": [">=", checkin_time.date()]
#         },
#         fields=["shift_type"]
#     )

#     attendance_type = "Off-Shift"  # default
#     overtime_hours = 0.0

#     # Check if checkin falls in any shift
#     for s in shifts:
#         shift_doc = frappe.get_doc("Shift Type", s.shift_type)
#         start, end = get_actual_start_end_datetime_of_shift(shift_doc, checkin_time)
#         if start <= checkin_time <= end:
#             attendance_type = "Normal Shift"
#             break

#     # Create / Update Attendance
#     if not frappe.db.exists("Attendance", {"employee": employee, "attendance_date": checkin_time.date()}):
#         attendance = frappe.get_doc({
#             "doctype": "Attendance",
#             "employee": employee,
#             "attendance_date": checkin_time.date(),
#             "status": "Present",
#             "attendance_type": attendance_type,
#             "overtime_hours": overtime_hours
#         })
#         attendance.insert(ignore_permissions=True)
#     else:
#         existing = frappe.get_doc("Attendance", {"employee": employee, "attendance_date": checkin_time.date()})
#         existing.attendance_type = attendance_type
#         existing.overtime_hours = overtime_hours
#         existing.save(ignore_permissions=True)









# # import frappe
# # from frappe.utils import now_datetime, get_datetime

# # @frappe.whitelist()   # expose to API
# # def mark_checkin(employee, log_type, latitude=None, longitude=None, geolocation=None, time=None):
# #     # ✅ Validate employee exists
# #     if not frappe.db.exists("Employee", employee):
# #         frappe.throw(f"Employee {employee} does not exist")

# #     # ✅ Validate log_type
# #     if log_type not in ["IN", "OUT"]:
# #         frappe.throw("Log type must be either IN or OUT")

# #     log_time = get_datetime(time) if time else now_datetime()

# #     # 1. Find if employee has a shift covering this time
# #     shift = frappe.db.sql("""
# #         SELECT sa.name, st.name as shift_type, st.start_time, st.end_time
# #         FROM `tabShift Assignment` sa
# #         JOIN `tabShift Type` st ON sa.shift_type = st.name
# #         WHERE sa.employee = %s
# #         AND sa.start_date <= %s
# #         AND (sa.end_date IS NULL OR sa.end_date >= %s)
# #     """, (employee, log_time.date(), log_time.date()), as_dict=True)

# #     if shift:
# #         shift_start = shift[0].start_time
# #         shift_end = shift[0].end_time

# #         if shift_start <= log_time.time() <= shift_end:
# #             log = frappe.get_doc({
# #                 "doctype": "Employee Checkin",
# #                 "employee": employee,
# #                 "time": log_time,
# #                 "log_type": log_type,
# #                 "latitude": latitude,
# #                 "longitude": longitude,
# #                 "geolocation": geolocation,
# #                 "shift": shift[0].shift_type,
# #                 "offshift": 0
# #             })
# #             log.insert(ignore_permissions=True)
# #             log.process_checkin_for_attendance()
# #             frappe.db.commit()

# #             return {
# #                 "employee": employee,
# #                 "log_type": log_type,
# #                 "time": str(log_time),
# #                 "shift": shift[0].shift_type,
# #                 "offshift": 0
# #             }

# #     # ❌ Outside shift
# #     off_log = frappe.get_doc({
# #         "doctype": "Employee Checkin",
# #         "employee": employee,
# #         "time": log_time,
# #         "log_type": log_type,
# #         "latitude": latitude,
# #         "longitude": longitude,
# #         "geolocation": geolocation,
# #         "shift": "Off-Shift",
# #         "offshift": 1
# #     })
# #     off_log.insert(ignore_permissions=True)

# #     if not frappe.db.exists("Attendance", {"employee": employee, "attendance_date": log_time.date()}):
# #         attendance = frappe.get_doc({
# #             "doctype": "Attendance",
# #             "employee": employee,
# #             "attendance_date": log_time.date(),
# #             "status": "Present",
# #             "shift": "Off-Shift",
# #             "offshift": 1,
# #             "latitude": latitude,
# #             "longitude": longitude,
# #             "geolocation": geolocation
# #         })
# #         attendance.insert(ignore_permissions=True)
# #         attendance.submit()

# #     frappe.db.commit()

# #     return {
# #         "employee": employee,
# #         "log_type": log_type,
# #         "time": str(log_time),
# #         "shift": "Off-Shift",
# #         "offshift": 1
# #     }