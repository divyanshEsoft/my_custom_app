import frappe
from frappe.utils import today

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
            # Count approved leave applications that fall within the allocation period
            consumed = frappe.db.count(
                "Leave Application",
                filters={
                    "employee": employee,
                    "leave_type": allocation.leave_type,
                    "docstatus": 1,  # only approved
                    "from_date": [">=", allocation.from_date],
                    "to_date": ["<=", allocation.to_date]
                }
            )

            balance = allocation.total_leaves_allocated - consumed

            leave_balances.append({
                "leave_type": allocation.leave_type,
                "total_allocated": allocation.total_leaves_allocated,
                "consumed": consumed,
                "balance": balance,
                "valid_from": allocation.from_date,
                "valid_to": allocation.to_date
            })

            # Running totals
            total_allocated += allocation.total_leaves_allocated
            total_consumed += consumed
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