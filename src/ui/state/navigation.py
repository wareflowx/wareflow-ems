"""Navigation and routing system for the Flet application."""

import flet as ft
from typing import Callable, Optional, Dict, Any


class Route:
    """Application route definitions."""

    # Dashboard/Alerts
    DASHBOARD = "/"

    # Employee management
    EMPLOYEES = "/employees"
    EMPLOYEE_DETAIL = "/employee/:id"

    # Documents
    DOCUMENTS = "/documents"

    # Settings
    SETTINGS = "/settings"


class NavigationHandler:
    """
    Handles navigation between views in the Flet application.

    Manages route changes, view switching, and maintains navigation history.
    """

    def __init__(self, page: ft.Page):
        """
        Initialize the navigation handler.

        Args:
            page: The Flet page instance
        """
        self.page = page
        self._view_map: Dict[str, Callable] = {}
        self._current_route: str = Route.DASHBOARD

    def register_view(self, route: str, view_builder: Callable[[ft.Page, Dict[str, Any]], ft.View]):
        """
        Register a view builder for a specific route.

        Args:
            route: The route pattern (e.g., "/employees")
            view_builder: Function that takes (page, route_args) and returns a ft.View
        """
        self._view_map[route] = view_builder

    def navigate(self, route: str, **kwargs):
        """
        Navigate to a specific route.

        Args:
            route: The route to navigate to
            **kwargs: Route parameters (e.g., id for "/employee/:id")
        """
        self._current_route = route

        # Find the matching view builder
        view_builder = self._find_view_builder(route)

        if view_builder:
            # Extract route arguments
            route_args = self._extract_route_args(route, kwargs)

            # Clear the page and add the new view
            self.page.views.clear()
            self.page.views.append(
                view_builder(self.page, route_args)
            )
            self.page.go(route)
        else:
            # If no view found, go to 404
            self._show_404(route)

    def go_back(self):
        """Navigate back to the previous view."""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def _find_view_builder(self, route: str) -> Optional[Callable]:
        """
        Find the appropriate view builder for a route.

        Args:
            route: The route pattern

        Returns:
            The view builder function or None if not found
        """
        # Direct match
        if route in self._view_map:
            return self._view_map[route]

        # Pattern match for dynamic routes (e.g., "/employee/:id")
        for pattern, builder in self._view_map.items():
            if self._route_matches_pattern(route, pattern):
                return builder

        return None

    def _route_matches_pattern(self, route: str, pattern: str) -> bool:
        """
        Check if a route matches a pattern.

        Args:
            route: The actual route (e.g., "/employee/123")
            pattern: The pattern to match (e.g., "/employee/:id")

        Returns:
            True if the route matches the pattern
        """
        route_parts = route.strip("/").split("/")
        pattern_parts = pattern.strip("/").split("/")

        if len(route_parts) != len(pattern_parts):
            return False

        for r_part, p_part in zip(route_parts, pattern_parts):
            if p_part.startswith(":"):
                # Dynamic parameter, matches anything
                continue
            elif r_part != p_part:
                # Static part doesn't match
                return False

        return True

    def _extract_route_args(self, route: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract route arguments from the route and kwargs.

        Args:
            route: The route string
            kwargs: Additional keyword arguments

        Returns:
            Dictionary of route arguments
        """
        args = {}

        # Find the matching pattern
        for pattern in self._view_map.keys():
            if self._route_matches_pattern(route, pattern):
                route_parts = route.strip("/").split("/")
                pattern_parts = pattern.strip("/").split("/")

                for i, p_part in enumerate(pattern_parts):
                    if p_part.startswith(":"):
                        param_name = p_part[1:]  # Remove the ":"
                        if i < len(route_parts):
                            args[param_name] = route_parts[i]

                # Also include any additional kwargs
                args.update(kwargs)
                break

        return args

    def _show_404(self, route: str):
        """
        Show a 404 not found view.

        Args:
            route: The route that was not found
        """
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                route,
                [
                    ft.AppBar(title=ft.Text("404 - Not Found")),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color=ft.colors.RED),
                                ft.Text(f"Route not found: {route}", size=20),
                                ft.ElevatedButton(
                                    "Go to Dashboard",
                                    on_click=lambda _: self.navigate(Route.DASHBOARD)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=20,
                        alignment=ft.alignment.center,
                    )
                ],
            )
        )
        self.page.update()

    @property
    def current_route(self) -> str:
        """Get the current route."""
        return self._current_route


def create_basic_view(
    route: str,
    title: str,
    content: ft.Control | None = None,
    actions: list[ft.Control] | None = None
) -> ft.View:
    """
    Create a basic view with AppBar.

    Args:
        route: The route for this view
        title: The title to display in the AppBar
        content: The main content of the view
        actions: Optional AppBar action buttons

    Returns:
        A configured ft.View instance
    """
    return ft.View(
        route,
        [
            ft.AppBar(
                title=ft.Text(title),
                actions=actions or [],
            ),
            ft.Container(
                content=content or ft.Text("Content coming soon..."),
                padding=20,
                expand=True,
            )
        ],
    )
