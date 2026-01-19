"""Employee controller - business logic for employee views."""

from typing import Dict, Any, Optional
from datetime import date

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from employee import queries, calculations


class EmployeeController:
    """
    Controller for Employee views.

    Orchestrates data fetching and business logic
    for employee detail and list views.
    """

    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID.

        Args:
            employee_id: Employee UUID as string

        Returns:
            Employee object or None if not found
        """
        try:
            return Employee.get_by_id(employee_id)
        except Employee.DoesNotExist:
            return None

    def get_employee_details(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete employee details for display.

        Args:
            employee_id: Employee UUID as string

        Returns:
            Dictionary with employee data or None if not found:
            {
                'employee': Employee,
                'compliance_score': int,
                'caces_list': List[Caces],
                'medical_visits': List[MedicalVisit],
                'trainings': List[OnlineTraining],
            }
        """
        emp = self.get_employee_by_id(employee_id)
        if not emp:
            return None

        # Get compliance score
        score_data = calculations.calculate_compliance_score(emp)

        # Get certifications with prefetch
        caces = list(emp.caces.order_by(-Caces.expiration_date))
        visits = list(emp.medical_visits.order_by(-MedicalVisit.visit_date))
        trainings = list(emp.online_trainings.order_by(-OnlineTraining.completed_date))

        return {
            'employee': emp,
            'compliance_score': score_data['score'],
            'score_breakdown': score_data['breakdown'],
            'caces_list': caces,
            'medical_visits': visits,
            'trainings': trainings,
        }

    def get_all_employees(self) -> list:
        """
        Get list of all employees for list view.

        Returns:
            List of Employee objects
        """
        return list(Employee.select().order_by(Employee.last_name, Employee.first_name))

    def get_active_employees(self) -> list:
        """
        Get list of active employees.

        Returns:
            List of active Employee objects
        """
        return list(Employee.select()
                    .where(Employee.current_status == 'active')
                    .order_by(Employee.last_name, Employee.first_name))
