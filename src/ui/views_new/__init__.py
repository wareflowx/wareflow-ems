"""Views registry - Connects view builders with router.

Import and register all application views with the routing system.
"""

import flet as ft
from ui.navigation.routes import register_view, Routes


def register_all_views():
    """Register all application views with the router."""

    # Dashboard view
    def build_dashboard(page: ft.Page, **kwargs) -> ft.Column:
        from ui.views_new.dashboard import DashboardView
        view = DashboardView(page)
        return view.build()

    register_view(Routes.DASHBOARD, build_dashboard)

    # Employees list view
    def build_employees(page: ft.Page, **kwargs) -> ft.Column:
        from ui.views_new.employees import EmployeesListView
        view = EmployeesListView(page)
        return view.build()

    register_view(Routes.EMPLOYEES, build_employees)

    # Employee detail view (placeholder - to be implemented)
    def build_employee_detail(page: ft.Page, id: str = None, **kwargs) -> ft.Column:
        from ui.views_new.employee_detail import EmployeeDetailView
        view = EmployeeDetailView(page, id)
        return view.build()

    register_view(Routes.EMPLOYEE_DETAIL, build_employee_detail)

    # Employee create view (placeholder - to be implemented)
    def build_employee_create(page: ft.Page, **kwargs) -> ft.Column:
        from ui.views_new.employee_form import EmployeeFormView
        view = EmployeeFormView(page, employee_id=None)
        return view.build()

    register_view(Routes.EMPLOYEE_CREATE, build_employee_create)

    # Alerts view (placeholder - to be implemented)
    def build_alerts(page: ft.Page, **kwargs) -> ft.Column:
        from ui.views_new.alerts import AlertsView
        view = AlertsView(page)
        return view.build()

    register_view(Routes.ALERTS, build_alerts)

    # Documents view (placeholder)
    def build_documents(page: ft.Page, **kwargs) -> ft.Column:
        from ui.views_new.documents import DocumentsView
        view = DocumentsView(page)
        return view.build()

    register_view(Routes.DOCUMENTS, build_documents)

    # Settings view (placeholder)
    def build_settings(page: ft.Page, **kwargs) -> ft.Column:
        from ui.views_new.settings import SettingsView
        view = SettingsView(page)
        return view.build()

    register_view(Routes.SETTINGS, build_settings)
