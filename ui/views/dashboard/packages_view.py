"""Packages view — list + add package dialog (with customer dropdown)."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import error_card, field, loading_center, section_header, show_snack, status_badge

_PRIORITIES = ["LOW", "MEDIUM", "HIGH"]


def _package_table(packages: list[dict]) -> ft.Control:
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
            alignment=ft.alignment.center,
            padding=ft.padding.all(40),
        )

    return ft.Row(
        [
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID",          weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Weight",      weight=ft.FontWeight.W_600), numeric=True),
                    ft.DataColumn(ft.Text("Priority",    weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Customer #",  weight=ft.FontWeight.W_600)),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(p["id"]))),
                        ft.DataCell(
                            ft.Text(p["description"], overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=1, width=200)
                        ),
                        ft.DataCell(ft.Text(f'{p["weight"]} kg')),
                        ft.DataCell(status_badge(p["priority"])),
                        ft.DataCell(ft.Text(str(p["customer_id"]))),
                    ])
                    for p in packages
                ],
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
    client = APIClient(page.session.get("token"))

    try:
        packages: list[dict] = await client.get("/packages/")
    except APIError:
        raise

    data_container = ft.Column([_package_table(packages)], expand=True)

    async def reload(_=None) -> None:
        data_container.controls = [loading_center()]
        await page.update_async()
        try:
            fresh = await client.get("/packages/")
            data_container.controls = [_package_table(fresh)]
        except APIError as exc:
            data_container.controls = [error_card(exc.message)]
        await page.update_async()

    async def open_add_dialog(_=None) -> None:
        # Fetch customers to populate the dropdown
        try:
            customers: list[dict] = await client.get("/customers/")
        except APIError as exc:
            show_snack(page, f"Could not load customers: {exc.message}", error=True)
            await page.update_async()
            return

        desc_f    = field("Description *", width=340)
        weight_f  = field("Weight (kg) *", keyboard_type=ft.KeyboardType.NUMBER, width=340)
        priority_dd = ft.Dropdown(
            label="Priority",
            value="MEDIUM",
            options=[ft.dropdown.Option(p) for p in _PRIORITIES],
            border_radius=8,
            width=340,
        )
        customer_dd = ft.Dropdown(
            label="Customer *",
            options=[
                ft.dropdown.Option(key=str(c["id"]), text=f"#{c['id']}  {c['name']}")
                for c in customers
            ],
            border_radius=8,
            width=340,
        )
        err_t    = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
        save_btn = ft.FilledButton("Add Package")
        progress = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        async def on_save(_=None) -> None:
            err_t.visible = False
            desc_f.error_text = weight_f.error_text = customer_dd.error_text = None
            has_err = False
            if not desc_f.value or not desc_f.value.strip():
                desc_f.error_text = "Required"
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
            if not customer_dd.value:
                customer_dd.error_text = "Select a customer"
                has_err = True
            if has_err:
                await page.update_async()
                return

            save_btn.disabled = True
            progress.visible  = True
            await page.update_async()

            try:
                await client.post("/packages/", json={
                    "description": desc_f.value.strip(),
                    "weight":      float(weight_f.value),
                    "priority":    priority_dd.value or "MEDIUM",
                    "customer_id": int(customer_dd.value),
                })
                dlg.open = False
                show_snack(page, "Package added.")
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
                [ft.Icon(ft.Icons.ADD_BOX_OUTLINED, color=ft.Colors.BLUE_400),
                 ft.Text("Add New Package")],
                spacing=10,
            ),
            content=ft.Column(
                [desc_f, weight_f, priority_dd, customer_dd, err_t],
                spacing=14, tight=True, width=356,
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

    return ft.Column(
        [
            ft.Row(
                [
                    section_header("Packages", "All registered shipment packages"),
                    ft.Row(
                        [
                            ft.OutlinedButton("Refresh", icon=ft.Icons.REFRESH, on_click=reload),
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
