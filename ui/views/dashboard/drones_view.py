"""Drones view — table with color-coded battery/status + register dialog."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import battery_widget, error_card, field, loading_center, section_header, show_snack, status_badge

_MODELS  = ["Lightweight", "Middleweight", "Cruiserweight", "Heavyweight"]
_STATUSES = ["IDLE", "LOADING", "DELIVERING", "DELIVERED", "RETURNING", "CHARGING"]


def _drone_table(drones: list[dict]) -> ft.Control:
    if not drones:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.FLIGHT_LAND, size=52, color=ft.Colors.GREY_700),
                    ft.Text("No drones registered yet.", color=ft.Colors.GREY_600, size=15),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.all(40),
        )

    return ft.Row(
        [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID",          weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Serial #",    weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Model",       weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Max Load",    weight=ft.FontWeight.W_600), numeric=True),
                    ft.DataColumn(ft.Text("Battery",     weight=ft.FontWeight.W_600), numeric=True),
                    ft.DataColumn(ft.Text("Status",      weight=ft.FontWeight.W_600)),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(d["id"]))),
                            ft.DataCell(ft.Text(d["serial_number"], weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(d["model"])),
                            ft.DataCell(ft.Text(f'{d["weight_limit"]} kg')),
                            ft.DataCell(battery_widget(d["battery_capacity"])),
                            ft.DataCell(status_badge(d["status"])),
                        ]
                    )
                    for d in drones
                ],
                border=ft.border.all(1, "#25FFFFFF"),
                border_radius=10,
                horizontal_lines=ft.BorderSide(1, "#15FFFFFF"),
                column_spacing=28,
                heading_row_color=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                heading_row_height=48,
                data_row_min_height=52,
                data_row_max_height=52,
            )
        ],
        scroll=ft.ScrollMode.AUTO,
    )


async def build_drones_view(page: ft.Page) -> ft.Control:
    client = APIClient(page.session.get("token"))

    # Initial fetch (awaited by shell — spinner already shown)
    try:
        drones: list[dict] = await client.get("/drones/")
    except APIError:
        raise

    data_container = ft.Column([_drone_table(drones)], expand=True)

    # ── reload ────────────────────────────────────────────────────────────────

    async def reload(_=None) -> None:
        data_container.controls = [loading_center()]
        await page.update_async()
        try:
            fresh = await client.get("/drones/")
            data_container.controls = [_drone_table(fresh)]
        except APIError as exc:
            data_container.controls = [error_card(exc.message)]
        await page.update_async()

    # ── register dialog ───────────────────────────────────────────────────────

    async def open_register_dialog(_=None) -> None:
        serial_f  = field("Serial Number *", hint_text="e.g. DR-001", width=320)
        model_dd  = ft.Dropdown(
            label="Model *",
            width=320,
            options=[ft.dropdown.Option(m) for m in _MODELS],
            border_radius=8,
        )
        weight_f  = field("Weight Limit (kg) *",
                          keyboard_type=ft.KeyboardType.NUMBER, width=320)
        battery_f = field("Battery Capacity (%)",
                          value="100",
                          keyboard_type=ft.KeyboardType.NUMBER, width=320)
        err_t     = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
        save_btn  = ft.FilledButton("Register")
        progress  = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        async def on_save(_=None) -> None:
            # ── validation ──
            err_t.visible = False
            serial_f.error_text = model_dd.error_text = weight_f.error_text = None

            has_err = False
            if not serial_f.value or not serial_f.value.strip():
                serial_f.error_text = "Required"
                has_err = True
            if not model_dd.value:
                model_dd.error_text = "Required"
                has_err = True
            if not weight_f.value:
                weight_f.error_text = "Required"
                has_err = True
            else:
                try:
                    float(weight_f.value)
                except ValueError:
                    weight_f.error_text = "Must be a number"
                    has_err = True

            if has_err:
                await page.update_async()
                return

            battery = 100
            if battery_f.value:
                try:
                    battery = int(battery_f.value)
                    if not 0 <= battery <= 100:
                        raise ValueError
                except ValueError:
                    battery_f.error_text = "Must be 0–100"
                    await page.update_async()
                    return

            save_btn.disabled = True
            progress.visible  = True
            await page.update_async()

            try:
                await client.post("/drones/", json={
                    "serial_number":  serial_f.value.strip(),
                    "model":          model_dd.value,
                    "weight_limit":   float(weight_f.value),
                    "battery_capacity": battery,
                })
                dlg.open = False
                show_snack(page, f"Drone '{serial_f.value.strip()}' registered.")
                await page.update_async()
                await reload()
            except APIError as exc:
                if exc.status_code == 401:
                    page.session.clear()
                    await page.go_async("/login")
                    return
                err_t.value   = exc.message
                err_t.visible = True
                save_btn.disabled = False
                progress.visible  = False
                await page.update_async()

        async def on_cancel(_=None) -> None:
            dlg.open = False
            await page.update_async()

        save_btn.on_click = on_save

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [ft.Icon(ft.Icons.FLIGHT, color=ft.Colors.BLUE_400), ft.Text("Register New Drone")],
                spacing=10,
            ),
            content=ft.Column(
                [serial_f, model_dd, weight_f, battery_f, err_t],
                spacing=14,
                tight=True,
                width=340,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=on_cancel),
                ft.Row([progress, save_btn], spacing=8, tight=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        await page.update_async()

    # ── layout ────────────────────────────────────────────────────────────────

    return ft.Column(
        [
            ft.Row(
                [
                    section_header("Drones", "All registered drones"),
                    ft.Row(
                        [
                            ft.OutlinedButton(
                                "Refresh",
                                icon=ft.Icons.REFRESH,
                                on_click=reload,
                            ),
                            ft.FilledButton(
                                "Register Drone",
                                icon=ft.Icons.ADD,
                                on_click=open_register_dialog,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(height=16),
            data_container,
        ],
        spacing=0,
        expand=True,
    )
