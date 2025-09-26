import frappe
from frappe.utils import today, date_diff, getdate

@frappe.whitelist(allow_guest=False)
def get_leave_type_balance_count(employee):
    """
    Get leave balances (allocated, consumed, balance) for the leave types allocated to an employee.
    """
    try:
        # Fetch all approved leave allocations for this employee
        allocations = frappe.get_all(
            "Leave Allocation",
            filters={"employee": employee, "docstatus": 1},
            fields=["leave_type", "total_leaves_allocated", "from_date", "to_date"]
        )

        leave_balances = []
        total_allocated = total_consumed = total_balance = 0

        for allocation in allocations:
            # Fetch approved leave applications for this leave type
            leave_apps = frappe.get_all(
                "Leave Application",
                filters={
                    "employee": employee,
                    "leave_type": allocation.leave_type,
                    "docstatus": 1  # only approved
                },
                fields=["from_date", "to_date"]
            )

            consumed_days = 0
            alloc_from = getdate(allocation.from_date)
            alloc_to = getdate(allocation.to_date)

            for leave in leave_apps:
                leave_from = getdate(leave.from_date)
                leave_to = getdate(leave.to_date)

                # Calculate overlapping days between allocation period and leave
                overlap_start = max(alloc_from, leave_from)
                overlap_end = min(alloc_to, leave_to)
                if overlap_start <= overlap_end:
                    consumed_days += date_diff(overlap_end, overlap_start) + 1

            balance = allocation.total_leaves_allocated - consumed_days

            leave_balances.append({
                "leave_type": allocation.leave_type,
                "total_allocated": allocation.total_leaves_allocated,
                "consumed": consumed_days,
                "balance": balance,
                "valid_from": allocation.from_date,
                "valid_to": allocation.to_date
            })

            # Running totals
            total_allocated += allocation.total_leaves_allocated
            total_consumed += consumed_days
            total_balance += balance

        return {
            "employee": employee,
            "leave_balances": leave_balances,
            "totals": {
                "allocated": total_allocated,
                "consumed": total_consumed,
                "balance": total_balance
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Leave Balance Fetch Error")
        return {"error": str(e)}




# import frappe
# from frappe.utils import today

# @frappe.whitelist(allow_guest=False)
# def get_leave_type_balance_count(employee):
#     """
#     Get leave balances (allocated, consumed, balance) for the leave types allocated to an employee.
#     """
#     try:
#         # Fetch all approved leave allocations for this employee
#         allocations = frappe.get_all(
#             "Leave Allocation",
#             filters={"employee": employee, "docstatus": 1},
#             fields=["leave_type", "total_leaves_allocated", "from_date", "to_date"]
#         )

#         leave_balances = []
#         total_allocated = total_consumed = total_balance = 0

#         for allocation in allocations:
#             # Count approved leave applications that fall within the allocation period
#             consumed = frappe.db.count(
#                 "Leave Application",
#                 filters={
#                     "employee": employee,
#                     "leave_type": allocation.leave_type,
#                     "docstatus": 1,  # only approved
#                     "from_date": [">=", allocation.from_date],
#                     "to_date": ["<=", allocation.to_date]
#                 }
#             )

#             balance = allocation.total_leaves_allocated - consumed

#             leave_balances.append({
#                 "leave_type": allocation.leave_type,
#                 "total_allocated": allocation.total_leaves_allocated,
#                 "consumed": consumed,
#                 "balance": balance,
#                 "valid_from": allocation.from_date,
#                 "valid_to": allocation.to_date
#             })

#             # Running totals
#             total_allocated += allocation.total_leaves_allocated
#             total_consumed += consumed
#             total_balance += balance

#         return {
#             "employee": employee,
#             "leave_balances": leave_balances,
#             "totals": {
#                 "allocated": total_allocated,
#                 "consumed": total_consumed,
#                 "balance": total_balance
#             }
#         }

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Leave Balance Fetch Error")
#         return {"error": str(e)}