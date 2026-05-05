"""Customers view — list + add customer dialog."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import error_card, field, loading_center, section_header, show_snack


def _customer_table(customers: list[dict]) -> ft.Control:
    if not customers:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=52, color=ft.Colors.GREY_700),
                    ft.Text("No customers yet.", color=ft.Colors.GREY_600, size=15),
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
                    ft.DataColumn(ft.Text("ID",      weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Name",    weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Email",   weight=ft.FontWeight.W_600)),
                    ft.DataColumn(ft.Text("Address", weight=ft.FontWeight.W_600)),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(c["id"]))),
                        ft.DataCell(ft.Text(c["name"], weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(c["email"])),
                        ft.DataCell(
                            ft.Text(c["address"], overflow=ft.TextOverflow.ELLIPSIS,
                                    max_lines=1, width=260)
                        ),
                    ])
                    for c in customers
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


async def build_customers_view(page: ft.Page) -> ft.Control:
    client = APIClient(page.session.get("token"))

    try:
        customers: list[dict] = await client.get("/customers/")
    except APIError:
        raise

    data_container = ft.Column([_customer_table(customers)], expand=True)

    async def reload(_=None) -> None:
        data_container.controls = [loading_center()]
        await page.update_async()
        try:
            fresh = await client.get("/customers/")
            data_container.controls = [_customer_table(fresh)]
        except APIError as exc:
            data_container.controls = [error_card(exc.message)]
        await page.update_async()

    async def open_add_dialog(_=None) -> None:
        name_f    = field("Full Name *",    width=340)
        email_f   = field("Email *",        keyboard_type=ft.KeyboardType.EMAIL, width=340)
        address_f = field("Address *",      width=340, min_lines=2, max_lines=3,
                          multiline=True, shift_enter=True)
        err_t     = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
        save_btn  = ft.FilledButton("Add Customer")
        progress  = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)

        async def on_save(_=None) -> None:
            err_t.visible = False
            name_f.error_text = email_f.error_text = address_f.error_text = None
            has_err = False
            if not name_f.value or not name_f.value.strip():
                name_f.error_text = "Required"
                has_err = True
            if not email_f.value or "@" not in email_f.value:
                email_f.error_text = "Enter a valid email"
                has_err = True
            if not address_f.value or not address_f.value.strip():
                address_f.error_text = "Required"
                has_err = True
            if has_err:
                await page.update_async()
                return

            save_btn.disabled = True
            progress.visible  = True
            await page.update_async()

            try:
                await client.post("/customers/", json={
                    "name":    name_f.value.strip(),
                    "email":   email_f.value.strip(),
                    "address": address_f.value.strip(),
                })
                dlg.open = False
                show_snack(page, f"Customer '{name_f.value.strip()}' added.")
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
                [ft.Icon(ft.Icons.PERSON_ADD, color=ft.Colors.BLUE_400),
                 ft.Text("Add New Customer")],
                spacing=10,
            ),
            content=ft.Column(
                [name_f, email_f, address_f, err_t],
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
                    section_header("Customers", "Registered delivery recipients"),
                    ft.Row(
                        [
                            ft.OutlinedButton("Refresh", icon=ft.Icons.REFRESH, on_click=reload),
                            ft.FilledButton("Add Customer", icon=ft.Icons.PERSON_ADD,
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
