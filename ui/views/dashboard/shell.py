"""Main dashboard shell: NavigationRail + swappable content area."""
from __future__ import annotations

from collections.abc import Coroutine
from typing import Any

import flet as ft

from ui.api.client import APIError
from ui.utils import loading_center, show_snack


# Deferred imports to avoid circular references at module load time
def _view_builders():
    from ui.views.dashboard.overview_view  import build_overview_view
    from ui.views.dashboard.drones_view    import build_drones_view
    from ui.views.dashboard.customers_view import build_customers_view
    from ui.views.dashboard.packages_view  import build_packages_view
    from ui.views.dashboard.routes_view    import build_routes_view
    from ui.views.dashboard.dispatch_view  import build_dispatch_view
    return [
        build_overview_view,
        build_drones_view,
        build_customers_view,
        build_packages_view,
        build_routes_view,
        build_dispatch_view,
    ]


_NAV_ITEMS = [
    (ft.Icons.DASHBOARD_OUTLINED,  ft.Icons.DASHBOARD,    "Overview"),
    (ft.Icons.FLIGHT_OUTLINED,     ft.Icons.FLIGHT,       "Drones"),
    (ft.Icons.PEOPLE_OUTLINE,      ft.Icons.PEOPLE,       "Customers"),
    (ft.Icons.INVENTORY_2_OUTLINED,ft.Icons.INVENTORY_2,  "Packages"),
    (ft.Icons.MAP_OUTLINED,        ft.Icons.MAP,          "Routes"),
    (ft.Icons.SEND_OUTLINED,       ft.Icons.SEND,         "Dispatch"),
]


def build_dashboard_shell(
    page: ft.Page,
) -> tuple[ft.View, Coroutine[Any, Any, None]]:
    """
    Returns ``(shell_view, init_coroutine)``.
    The caller must ``await init_coroutine()`` after the view is rendered.
    """
    content = ft.Column(
        [loading_center()],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    nav_rail = ft.NavigationRail(
        destinations=[
            ft.NavigationRailDestination(
                icon=idle, selected_icon=active, label=label
            )
            for idle, active, label in _NAV_ITEMS
        ],
        selected_index=0,
        extended=True,
        min_width=72,
        min_extended_width=180,
        group_alignment=-1.0,
    )

    # ── loading helper ────────────────────────────────────────────────────────

    async def load_view(index: int) -> None:
        content.controls = [loading_center()]
        await page.update_async()

        builders = _view_builders()
        try:
            ctrl = await builders[index](page)
            content.controls = [ctrl]
        except APIError as exc:
            if exc.status_code == 401:
                page.session.clear()
                await page.go_async("/login")
                return
            show_snack(page, exc.message, error=True)
            from ui.utils import error_card
            content.controls = [error_card(exc.message)]
        except Exception as exc:
            from ui.utils import error_card
            content.controls = [error_card(str(exc))]

        await page.update_async()

    # ── navigation handler ────────────────────────────────────────────────────

    async def on_nav_change(e: ft.ControlEvent) -> None:
        await load_view(e.control.selected_index)

    nav_rail.on_change = on_nav_change

    # ── logout ────────────────────────────────────────────────────────────────

    async def on_logout(_: ft.ControlEvent) -> None:
        page.session.clear()
        await page.go_async("/login")

    username = page.session.get("username") or "User"

    # ── view ──────────────────────────────────────────────────────────────────

    shell_view = ft.View(
        route="/dashboard",
        controls=[
            ft.Row(
                [
                    nav_rail,
                    ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE),
                    ft.Container(content=content, expand=True, padding=ft.padding.all(24)),
                ],
                expand=True,
                spacing=0,
            )
        ],
        appbar=ft.AppBar(
            leading=ft.Icon(ft.Icons.FLIGHT_TAKEOFF, color=ft.Colors.BLUE_400),
            leading_width=48,
            title=ft.Text(
                "Drone Dispatch Portal",
                weight=ft.FontWeight.BOLD,
                size=18,
            ),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                                    color=ft.Colors.GREY_400, size=20),
                            ft.Text(username, size=13, color=ft.Colors.GREY_300),
                        ],
                        spacing=6,
                    ),
                    padding=ft.padding.only(right=8),
                ),
                ft.IconButton(
                    ft.Icons.LOGOUT,
                    tooltip="Sign out",
                    on_click=on_logout,
                    icon_color=ft.Colors.GREY_400,
                ),
                ft.Container(width=4),
            ],
        ),
        padding=0,
    )

    async def init() -> None:
        await load_view(0)

    return shell_view, init
