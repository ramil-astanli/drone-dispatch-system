"""Dispatch console — elect best drone for a package and create a route."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import field, section_header, show_snack, status_badge


async def build_dispatch_view(page: ft.Page) -> ft.Control:
    client = APIClient(page.session.get("token"))

    # Fetch packages for the dropdown
    try:
        packages: list[dict] = await client.get("/packages/")
    except APIError:
        raise

    # ── form controls ─────────────────────────────────────────────────────────
    pkg_dd = ft.Dropdown(
        label="Select Package *",
        hint_text="Choose the package to dispatch",
        options=[
            ft.dropdown.Option(
                key=str(p["id"]),
                text=(
                    f"#{p['id']}  —  {p['description']}"
                    f"  ({p['weight']} kg, {p['priority']})"
                ),
            )
            for p in packages
        ],
        border_radius=8,
    )
    origin_f = field(
        "Origin Address *",
        hint_text="e.g. Central Depot, 1 Warehouse Blvd",
        prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
    )
    dest_f = field(
        "Destination Address *",
        hint_text="e.g. 42 Maple Street, Springfield",
        prefix_icon=ft.Icons.FLAG_OUTLINED,
    )

    dispatch_btn = ft.FilledButton(
        "Dispatch Package",
        icon=ft.Icons.SEND,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
        ),
    )
    progress  = ft.ProgressRing(width=22, height=22, stroke_width=3, visible=False)
    err_t     = ft.Text("", color=ft.Colors.RED_400, size=13, visible=False)

    # Holds the card list of recent dispatches (newest first)
    history   = ft.Column(spacing=8)

    # ── refresh packages list ─────────────────────────────────────────────────

    async def refresh_packages(_=None) -> None:
        try:
            fresh = await client.get("/packages/")
            pkg_dd.options = [
                ft.dropdown.Option(
                    key=str(p["id"]),
                    text=(
                        f"#{p['id']}  —  {p['description']}"
                        f"  ({p['weight']} kg, {p['priority']})"
                    ),
                )
                for p in fresh
            ]
            pkg_dd.value = None
            await page.update_async()
        except APIError as exc:
            show_snack(page, exc.message, error=True)
            await page.update_async()

    # ── dispatch handler ──────────────────────────────────────────────────────

    async def on_dispatch(_=None) -> None:
        err_t.visible     = False
        pkg_dd.error_text = origin_f.error_text = dest_f.error_text = None

        has_err = False
        if not pkg_dd.value:
            pkg_dd.error_text = "Select a package"
            has_err = True
        if not origin_f.value or not origin_f.value.strip():
            origin_f.error_text = "Required"
            has_err = True
        if not dest_f.value or not dest_f.value.strip():
            dest_f.error_text = "Required"
            has_err = True

        if has_err:
            await page.update_async()
            return

        dispatch_btn.disabled = True
        progress.visible      = True
        await page.update_async()

        try:
            route = await client.post("/dispatch/", json={
                "package_id":         int(pkg_dd.value),
                "origin_address":     origin_f.value.strip(),
                "destination_address": dest_f.value.strip(),
            })

            # ── success card ──────────────────────────────────────────────────
            history.controls.insert(
                0,
                ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        ft.Icons.CHECK_CIRCLE_OUTLINED,
                                        color=ft.Colors.GREEN_400,
                                        size=28,
                                    ),
                                    padding=ft.padding.only(right=4),
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"Route #{route['id']} created",
                                            weight=ft.FontWeight.W_600,
                                            size=14,
                                        ),
                                        ft.Text(
                                            f"Drone #{route.get('drone_id', '—')}  ·  "
                                            f"{route['origin_address']}  →  "
                                            f"{route['destination_address']}",
                                            size=12,
                                            color=ft.Colors.GREY_400,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=3,
                                    expand=True,
                                ),
                                status_badge(route["status"]),
                            ],
                            spacing=12,
                        ),
                        padding=ft.padding.symmetric(horizontal=18, vertical=14),
                    ),
                    elevation=3,
                ),
            )

            # Reset form
            pkg_dd.value      = None
            origin_f.value    = ""
            dest_f.value      = ""
            show_snack(page, f"Package dispatched! Route #{route['id']} created.")

        except APIError as exc:
            if exc.status_code == 401:
                page.session.clear()
                await page.go_async("/login")
                return
            err_t.value   = exc.message
            err_t.visible = True

        finally:
            dispatch_btn.disabled = False
            progress.visible      = False
            await page.update_async()

    dispatch_btn.on_click = on_dispatch

    # ── empty history placeholder ─────────────────────────────────────────────
    history.controls = [
        ft.Container(
            content=ft.Text(
                "Dispatched routes will appear here.",
                color=ft.Colors.GREY_600,
                size=13,
                italic=True,
            ),
            padding=ft.padding.only(top=4),
        )
    ]

    # ── layout ────────────────────────────────────────────────────────────────
    return ft.Column(
        [
            section_header("Dispatch Console", "Assign the best available drone to a package"),
            ft.Container(height=8),

            # ── dispatch form card ────────────────────────────────────────────
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.SEARCH, color=ft.Colors.GREY_500, size=18),
                                    ft.Text("Package", size=13, color=ft.Colors.GREY_500),
                                    ft.Container(expand=True),
                                    ft.TextButton(
                                        "Refresh list",
                                        icon=ft.Icons.REFRESH,
                                        on_click=refresh_packages,
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.GREY_500,
                                        ),
                                    ),
                                ],
                                spacing=6,
                            ),
                            pkg_dd,
                            ft.Divider(height=8),
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.LOCATION_ON_OUTLINED,
                                            color=ft.Colors.GREY_500, size=18),
                                    ft.Text("Addresses", size=13, color=ft.Colors.GREY_500),
                                ],
                                spacing=6,
                            ),
                            origin_f,
                            dest_f,
                            err_t,
                            ft.Container(height=4),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Row(
                                                    [ft.Icon(ft.Icons.INFO_OUTLINE,
                                                             color=ft.Colors.BLUE_300, size=15),
                                                     ft.Text(
                                                         "The system will select the IDLE drone with "
                                                         "the highest battery (> 25 %).",
                                                         size=12,
                                                         color=ft.Colors.GREY_500,
                                                     )],
                                                    spacing=6,
                                                )
                                            ]
                                        ),
                                        expand=True,
                                    ),
                                    ft.Row([progress, dispatch_btn], spacing=10, tight=True),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=14,
                    ),
                    padding=ft.padding.all(24),
                ),
                elevation=4,
            ),

            ft.Container(height=8),
            ft.Text("Dispatch History (this session)", size=16,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=4),
            history,
        ],
        spacing=8,
        expand=True,
    )
