"""Drones view — table with color-coded battery/status + register / edit / delete."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import battery_widget, error_card, field, loading_center, section_header, show_snack, status_badge

_MODELS   = ["Lightweight", "Middleweight", "Cruiserweight", "Heavyweight"]
_STATUSES = ["IDLE", "LOADING", "DELIVERING", "DELIVERED", "RETURNING"]


def _drone_table(drones: list[dict], on_edit, on_delete) -> ft.Control:
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
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(40),
        )

    def _make_row(d: dict) -> ft.DataRow:
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(d["id"]))),
            ft.DataCell(ft.Text(d["serial_number"], weight=ft.FontWeight.W_500)),
            ft.DataCell(ft.Text(d["model"])),
            ft.DataCell(ft.Text(f'{d["weight_limit"]} kg')),
            ft.DataCell(battery_widget(d["battery_capacity"])),
            ft.DataCell(status_badge(d["status"])),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        ft.Icons.EDIT_OUTLINED,
                        icon_color=ft.Colors.BLUE_300,
                        tooltip="Edit",
                        on_click=lambda _, drone=d: on_edit(drone),
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_300,
                        tooltip="Delete",
                        on_click=lambda _, drone=d: on_delete(drone),
                    ),
                ], spacing=0, tight=True)
            ),
        ])

    return ft.Row(
        [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID",       weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Serial #", weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Model",    weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Max Load", weight=ft.FontWeight.W_600), numeric=True),
                    ft.DataColumn(ft.Text("Battery",  weight=ft.FontWeight.W_600), numeric=True),
                    ft.DataColumn(ft.Text("Status",   weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Actions",  weight=ft.FontWeight.W_600)),
                ],
                rows=[_make_row(d) for d in drones],
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
    client = APIClient()

    try:
        drones: list[dict] = await client.get("/drones/")
    except APIError:
        raise

    data_container = ft.Column(expand=True)

    def _close(dlg: ft.AlertDialog) -> None:
        dlg.open = False
        page.update()

    async def reload(_=None) -> None:
        data_container.controls = [loading_center()]
        page.update()
        try:
            fresh = await client.get("/drones/")
            _refresh_table(fresh)
        except APIError as exc:
            data_container.controls = [error_card(exc.message)]
        page.update()

    async def open_add_dialog(_=None) -> None:
        serial_f  = field("Serial Number *", hint_text="e.g. DR-001", width=320)
        model_dd  = ft.Dropdown(
            label="Model *", width=320,
            options=[ft.dropdown.Option(m) for m in _MODELS],
            border_radius=8,
        )
        weight_f  = field("Weight Limit (kg) *",
                          keyboard_type=ft.KeyboardType.NUMBER, width=320)
        battery_f = field("Battery Capacity (%)", value="100",
                          keyboard_type=ft.KeyboardType.NUMBER, width=320)
        err_t    = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
        save_btn = ft.FilledButton("Add")
        progress = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        async def on_save(_=None) -> None:
            err_t.visible = False
            serial_f.error_text = model_dd.error_text = weight_f.error_text = None

            has_err = False
            if not serial_f.value or not serial_f.value.strip():
                serial_f.error_text = "Required"; has_err = True
            if not model_dd.value:
                model_dd.error_text = "Required"; has_err = True
            if not weight_f.value:
                weight_f.error_text = "Required"; has_err = True
            else:
                try:
                    float(weight_f.value)
                except ValueError:
                    weight_f.error_text = "Must be a number"; has_err = True

            if has_err:
                page.update()
                return

            battery = 100
            if battery_f.value:
                try:
                    battery = int(battery_f.value)
                    if not 0 <= battery <= 100:
                        raise ValueError
                except ValueError:
                    battery_f.error_text = "Must be 0–100"
                    page.update()
                    return

            save_btn.disabled = True
            progress.visible  = True
            page.update()

            try:
                await client.post("/drones/", json={
                    "serial_number":    serial_f.value.strip(),
                    "model":            model_dd.value,
                    "weight_limit":     float(weight_f.value),
                    "battery_capacity": battery,
                })
                dlg.open = False
                show_snack(page, f"Drone '{serial_f.value.strip()}' added.")
                page.update()
                await reload()
            except APIError as exc:
                err_t.value       = exc.message
                err_t.visible     = True
                save_btn.disabled = False
                progress.visible  = False
                page.update()

        save_btn.on_click = on_save

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [ft.Icon(ft.Icons.FLIGHT, color=ft.Colors.BLUE_400),
                 ft.Text("Add New Drone")],
                spacing=10,
            ),
            content=ft.Column(
                [serial_f, model_dd, weight_f, battery_f, err_t],
                spacing=14, tight=True, width=340,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: _close(dlg)),
                ft.Row([progress, save_btn], spacing=8, tight=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def on_edit(drone: dict) -> None:
        model_dd  = ft.Dropdown(
            label="Model", value=drone["model"], width=320,
            options=[ft.dropdown.Option(m) for m in _MODELS],
            border_radius=8,
        )
        status_dd = ft.Dropdown(
            label="Status", value=drone["status"], width=320,
            options=[ft.dropdown.Option(s) for s in _STATUSES],
            border_radius=8,
        )
        weight_f  = field("Weight Limit (kg) *", value=str(drone["weight_limit"]),
                          keyboard_type=ft.KeyboardType.NUMBER, width=320)
        battery_f = field("Battery Capacity (%)", value=str(drone["battery_capacity"]),
                          keyboard_type=ft.KeyboardType.NUMBER, width=320)
        err_t    = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
        save_btn = ft.FilledButton("Save Changes")
        progress = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        async def on_save(_=None) -> None:
            err_t.visible = False
            weight_f.error_text = battery_f.error_text = None
            has_err = False

            if not weight_f.value:
                weight_f.error_text = "Required"; has_err = True
            else:
                try:
                    float(weight_f.value)
                except ValueError:
                    weight_f.error_text = "Must be a number"; has_err = True

            battery = drone["battery_capacity"]
            if battery_f.value:
                try:
                    battery = int(battery_f.value)
                    if not 0 <= battery <= 100:
                        raise ValueError
                except ValueError:
                    battery_f.error_text = "Must be 0–100"; has_err = True

            if has_err:
                page.update()
                return

            save_btn.disabled = True
            progress.visible  = True
            page.update()

            try:
                await client.patch(f"/drones/{drone['id']}", json={
                    "model":            model_dd.value or drone["model"],
                    "status":           status_dd.value or drone["status"],
                    "weight_limit":     float(weight_f.value),
                    "battery_capacity": battery,
                })
                dlg.open = False
                show_snack(page, f"Drone #{drone['id']} updated.")
                page.update()
                await reload()
            except APIError as exc:
                err_t.value       = exc.message
                err_t.visible     = True
                save_btn.disabled = False
                progress.visible  = False
                page.update()

        save_btn.on_click = on_save

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [ft.Icon(ft.Icons.EDIT, color=ft.Colors.BLUE_400),
                 ft.Text(f"Edit Drone #{drone['id']}  ({drone['serial_number']})")],
                spacing=10,
            ),
            content=ft.Column(
                [model_dd, status_dd, weight_f, battery_f, err_t],
                spacing=14, tight=True, width=340,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: _close(dlg)),
                ft.Row([progress, save_btn], spacing=8, tight=True),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def on_delete(drone: dict) -> None:
        async def confirm(_=None) -> None:
            try:
                await client.delete(f"/drones/{drone['id']}")
                dlg.open = False
                show_snack(page, f"Drone {drone['serial_number']} deleted.")
                page.update()
                await reload()
            except APIError as exc:
                dlg.open = False
                show_snack(page, exc.message, error=True)
                page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_400),
                 ft.Text("Delete Drone")],
                spacing=10,
            ),
            content=ft.Text(
                f"Delete drone {drone['serial_number']}?\nThis action cannot be undone.",
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: _close(dlg)),
                ft.FilledButton(
                    "Delete", style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700),
                    on_click=confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def _refresh_table(data: list[dict]) -> None:
        data_container.controls = [_drone_table(data, on_edit, on_delete)]

    _refresh_table(drones)

    return ft.Column(
        [
            ft.Row(
                [
                    section_header("Drones", "All registered drones"),
                    ft.Row(
                        [
                            ft.OutlinedButton("Refresh", icon=ft.Icons.REFRESH,
                                              on_click=reload),
                            ft.FilledButton("Add Drone", icon=ft.Icons.ADD,
                                            on_click=open_add_dialog),
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
