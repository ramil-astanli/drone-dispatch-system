"""Packages view — list + add / edit / delete package."""
from __future__ import annotations

import flet as ft

import ui.state as state
from ui.api.client import APIClient, APIError
from ui.utils import error_card, field, loading_center, section_header, show_snack, status_badge

_PRIORITIES = ["LOW", "MEDIUM", "HIGH"]


def _package_table(packages: list[dict], on_edit, on_delete) -> ft.Control:
    if not packages:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=52, color=ft.Colors.GREY_700),
                    ft.Text("No packages yet.", color=ft.Colors.GREY_600, size=15),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.all(40),
        )

    def _make_row(p: dict) -> ft.DataRow:
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(p["id"]))),
            ft.DataCell(
                ft.Text(p["description"], overflow=ft.TextOverflow.ELLIPSIS,
                        max_lines=1, width=180)
            ),
            ft.DataCell(ft.Text(f'{p["weight"]} kg')),
            ft.DataCell(status_badge(p["priority"])),
            ft.DataCell(ft.Text(str(p["customer_id"]))),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(
                        ft.Icons.EDIT_OUTLINED,
                        icon_color=ft.Colors.BLUE_300,
                        tooltip="Edit",
                        on_click=lambda _, pkg=p: on_edit(pkg),
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_300,
                        tooltip="Delete",
                        on_click=lambda _, pkg=p: on_delete(pkg),
                    ),
                ], spacing=0, tight=True)
            ),
        ])

    return ft.Row(
        [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID",          weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Weight",      weight=ft.FontWeight.W_600), numeric=True),
                    ft.DataColumn(ft.Text("Priority",    weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Customer #",  weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Actions",     weight=ft.FontWeight.W_600)),
                ],
                rows=[_make_row(p) for p in packages],
                border=ft.border.all(1, "#25FFFFFF"),
                border_radius=10,
                horizontal_lines=ft.BorderSide(1, "#15FFFFFF"),
                column_spacing=28,
                heading_row_color=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                heading_row_height=48,
                data_row_min_height=52,
            )
        ],
        scroll=ft.ScrollMode.AUTO,
    )


async def build_packages_view(page: ft.Page) -> ft.Control:
    client = APIClient()

    try:
        packages: list[dict] = await client.get("/packages/")
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
            fresh = await client.get("/packages/")
            data_container.controls = [_package_table(fresh, on_edit, on_delete)]
        except APIError as exc:
            data_container.controls = [error_card(exc.message)]
        page.update()

    async def open_add_dialog(_=None) -> None:
        try:
            customers: list[dict] = await client.get("/customers/")
        except APIError as exc:
            show_snack(page, f"Could not load customers: {exc.message}", error=True)
            page.update()
            return

        desc_f      = field("Description *", width=340)
        weight_f    = field("Weight (kg) *", keyboard_type=ft.KeyboardType.NUMBER, width=340)
        priority_dd = ft.Dropdown(
            label="Priority", value="MEDIUM",
            options=[ft.dropdown.Option(p) for p in _PRIORITIES],
            border_radius=8, width=340,
        )
        customer_dd = ft.Dropdown(
            label="Customer *",
            options=[
                ft.dropdown.Option(key=str(c["id"]), text=f"#{c['id']}  {c['name']}")
                for c in customers
            ],
            border_radius=8, width=340,
        )
        err_t    = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
        save_btn = ft.FilledButton("Add Package")
        progress = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        async def on_save(_=None) -> None:
            err_t.visible = False
            desc_f.error_text = weight_f.error_text = customer_dd.error_text = None
            has_err = False
            if not desc_f.value or not desc_f.value.strip():
                desc_f.error_text = "Required"; has_err = True
            if not weight_f.value:
                weight_f.error_text = "Required"; has_err = True
            else:
                try:
                    float(weight_f.value)
                except ValueError:
                    weight_f.error_text = "Must be a number"; has_err = True
            if not customer_dd.value:
                customer_dd.error_text = "Select a customer"; has_err = True
            if has_err:
                page.update()
                return

            save_btn.disabled = True
            progress.visible  = True
            page.update()

            try:
                await client.post("/packages/", json={
                    "description": desc_f.value.strip(),
                    "weight":      float(weight_f.value),
                    "priority":    priority_dd.value or "MEDIUM",
                    "customer_id": int(customer_dd.value),
                })
                dlg.open = False
                show_snack(page, "Package added.")
                page.update()
                await reload()
            except APIError as exc:
                if exc.status_code == 401:
                    state.clear()
                    await page.push_route("/login")
                    return
                err_t.value       = exc.message
                err_t.visible     = True
                save_btn.disabled = False
                progress.visible  = False
                page.update()

        save_btn.on_click = on_save

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [ft.Icon(ft.Icons.ADD_BOX_OUTLINED, color=ft.Colors.BLUE_400),
                 ft.Text("Add New Package")],
                spacing=10,
            ),
            content=ft.Column(
                [desc_f, weight_f, priority_dd, customer_dd, err_t],
                spacing=14, tight=True, width=356,
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

    def on_edit(pkg: dict) -> None:
        desc_f      = field("Description *", value=pkg["description"], width=340)
        weight_f    = field("Weight (kg) *", value=str(pkg["weight"]),
                            keyboard_type=ft.KeyboardType.NUMBER, width=340)
        priority_dd = ft.Dropdown(
            label="Priority", value=pkg["priority"],
            options=[ft.dropdown.Option(p) for p in _PRIORITIES],
            border_radius=8, width=340,
        )
        err_t    = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
        save_btn = ft.FilledButton("Save Changes")
        progress = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        async def on_save(_=None) -> None:
            err_t.visible = False
            desc_f.error_text = weight_f.error_text = None
            has_err = False
            if not desc_f.value or not desc_f.value.strip():
                desc_f.error_text = "Required"; has_err = True
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

            save_btn.disabled = True
            progress.visible  = True
            page.update()

            try:
                await client.patch(f"/packages/{pkg['id']}", json={
                    "description": desc_f.value.strip(),
                    "weight":      float(weight_f.value),
                    "priority":    priority_dd.value or pkg["priority"],
                })
                dlg.open = False
                show_snack(page, f"Package #{pkg['id']} updated.")
                page.update()
                await reload()
            except APIError as exc:
                if exc.status_code == 401:
                    state.clear()
                    page.run_task(page.push_route, "/login")
                    return
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
                 ft.Text(f"Edit Package #{pkg['id']}")],
                spacing=10,
            ),
            content=ft.Column(
                [desc_f, weight_f, priority_dd, err_t],
                spacing=14, tight=True, width=356,
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

    def on_delete(pkg: dict) -> None:
        async def confirm(_=None) -> None:
            try:
                await client.delete(f"/packages/{pkg['id']}")
                dlg.open = False
                show_snack(page, f"Package #{pkg['id']} deleted.")
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
                 ft.Text("Delete Package")],
                spacing=10,
            ),
            content=ft.Text(
                f"Delete package #{pkg['id']}?\nThis action cannot be undone.",
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

    data_container.controls = [_package_table(packages, on_edit, on_delete)]

    return ft.Column(
        [
            ft.Row(
                [
                    section_header("Packages", "All registered shipment packages"),
                    ft.Row(
                        [
                            ft.OutlinedButton("Refresh", icon=ft.Icons.REFRESH,
                                              on_click=reload),
                            ft.FilledButton("Add Package", icon=ft.Icons.ADD,
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
