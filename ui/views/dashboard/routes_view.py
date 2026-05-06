"""Routes monitoring view — read-only table with status and timestamps."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import error_card, loading_center, section_header, status_badge


def _format_ts(ts: str | None) -> str:
    if not ts:
        return "—"
    # ISO format: "2024-01-15T14:32:00+00:00"  →  "2024-01-15  14:32"
    try:
        date, time = ts[:19].split("T")
        return f"{date}  {time[:5]}"
    except Exception:
        return ts[:16]


def _routes_table(routes: list[dict]) -> ft.Control:
    if not routes:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.MAP_OUTLINED, size=52, color=ft.Colors.GREY_700),
                    ft.Text("No routes found.", color=ft.Colors.GREY_600, size=15),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(40),
        )

    return ft.Row(
        [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID",          weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Drone #",     weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Package #",   weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Origin",      weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Destination", weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Status",      weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Created",     weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Completed",   weight=ft.FontWeight.W_600)),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(r["id"]))),
                            ft.DataCell(ft.Text(str(r.get("drone_id") or "—"))),
                            ft.DataCell(ft.Text(str(r["package_id"]))),
                            ft.DataCell(
                                ft.Text(r["origin_address"],
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=1, width=160)
                            ),
                            ft.DataCell(
                                ft.Text(r["destination_address"],
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        max_lines=1, width=160)
                            ),
                            ft.DataCell(status_badge(r["status"])),
                            ft.DataCell(ft.Text(_format_ts(r.get("created_at")),
                                                size=12, color=ft.Colors.GREY_400)),
                            ft.DataCell(ft.Text(_format_ts(r.get("completed_at")),
                                                size=12, color=ft.Colors.GREY_400)),
                        ],
                        color=ft.Colors.with_opacity(
                            0.06 if r["status"] == "IN_PROGRESS" else 0,
                            ft.Colors.BLUE,
                        ),
                    )
                    for r in routes
                ],
                border=ft.border.all(1, "#25FFFFFF"),
                border_radius=10,
                horizontal_lines=ft.BorderSide(1, "#15FFFFFF"),
                column_spacing=24,
                heading_row_color=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                heading_row_height=48,
                data_row_min_height=52,
            )
        ],
        scroll=ft.ScrollMode.AUTO,
    )


async def build_routes_view(page: ft.Page) -> ft.Control:
    client = APIClient()

    try:
        routes: list[dict] = await client.get("/routes/")
    except APIError:
        raise

    # Sort: active first, then by id descending
    routes.sort(
        key=lambda r: (r["status"] not in ("PENDING", "IN_PROGRESS"), -r["id"])
    )

    data_container = ft.Column([_routes_table(routes)], expand=True)

    legend = ft.Row(
        [
            ft.Text("Status guide:", size=12, color=ft.Colors.GREY_500),
            *[status_badge(s) for s in ("PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED")],
        ],
        spacing=8,
    )

    async def reload(_=None) -> None:
        data_container.controls = [loading_center()]
        page.update()
        try:
            fresh = await client.get("/routes/")
            fresh.sort(
                key=lambda r: (r["status"] not in ("PENDING", "IN_PROGRESS"), -r["id"])
            )
            data_container.controls = [_routes_table(fresh)]
        except APIError as exc:
            data_container.controls = [error_card(exc.message)]
        page.update()

    return ft.Column(
        [
            ft.Row(
                [
                    section_header("Routes", "Delivery route monitoring"),
                    ft.OutlinedButton("Refresh", icon=ft.Icons.REFRESH, on_click=reload),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            legend,
            ft.Divider(height=12),
            data_container,
        ],
        spacing=8,
        expand=True,
    )
