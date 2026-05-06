"""Overview dashboard — stat cards + recent routes summary."""
from __future__ import annotations

import asyncio

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import section_header, stat_card, status_badge


async def build_overview_view(page: ft.Page) -> ft.Control:
    client = APIClient()

    try:
        drones, available, packages, routes = await asyncio.gather(
            client.get("/drones/"),
            client.get("/drones/available"),
            client.get("/packages/"),
            client.get("/routes/"),
        )
    except APIError:
        raise  # Re-raise so the shell can handle 401 redirect

    active_routes = [r for r in routes if r["status"] in ("PENDING", "IN_PROGRESS")]

    # ── stat cards ────────────────────────────────────────────────────────────
    cards_row = ft.Row(
        [
            stat_card(ft.Icons.FLIGHT,         "Total Drones",   str(len(drones)),    ft.Colors.BLUE_400),
            stat_card(ft.Icons.CHECK_CIRCLE,   "Available Now",  str(len(available)), ft.Colors.GREEN_400),
            stat_card(ft.Icons.INVENTORY_2,    "Total Packages", str(len(packages)),  ft.Colors.ORANGE_400),
            stat_card(ft.Icons.ROUTE,          "Active Routes",  str(len(active_routes)), ft.Colors.PURPLE_400),
        ],
        wrap=True,
        spacing=16,
        run_spacing=16,
    )

    # ── recent routes ─────────────────────────────────────────────────────────
    recent = sorted(routes, key=lambda r: r.get("created_at", ""), reverse=True)[:8]

    route_tiles = [
        ft.Card(
            content=ft.ListTile(
                leading=ft.Container(
                    content=ft.Icon(ft.Icons.ROUTE, size=20),
                    bgcolor=ft.Colors.BLUE_900,
                    border_radius=8,
                    padding=ft.Padding.all(6),
                ),
                title=ft.Text(
                    f"Route #{r['id']}  —  {r['origin_address']} → {r['destination_address']}",
                    size=13,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                subtitle=ft.Text(
                    f"Drone #{r.get('drone_id', '—')}   ·   Package #{r['package_id']}",
                    size=12,
                    color=ft.Colors.GREY_500,
                ),
                trailing=status_badge(r["status"]),
            ),
            elevation=2,
        )
        for r in recent
    ]

    empty_routes = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.INBOX_OUTLINED, size=48, color=ft.Colors.GREY_700),
                ft.Text("No routes yet.", color=ft.Colors.GREY_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.all(32),
    )

    return ft.Column(
        [
            section_header("Overview", "Live snapshot of your fleet"),
            ft.Container(height=8),
            cards_row,
            ft.Divider(height=32),
            ft.Text("Recent Routes", size=17, weight=ft.FontWeight.W_600),
            ft.Container(height=4),
            *(route_tiles if route_tiles else [empty_routes]),
        ],
        spacing=8,
        expand=True,
    )
