"""Login screen."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import field


def build_login_view(page: ft.Page) -> ft.View:
    username_f = field("Username", prefix_icon=ft.Icons.PERSON_OUTLINE,
                       autofocus=True, width=340)
    password_f = field("Password", prefix_icon=ft.Icons.LOCK_OUTLINE,
                       password=True, can_reveal_password=True, width=340)
    status_t   = ft.Text("", color=ft.Colors.RED_400, size=13, visible=False)
    progress   = ft.ProgressBar(visible=False, width=340, color=ft.Colors.BLUE_400)
    login_btn  = ft.FilledButton("Sign In", icon=ft.Icons.LOGIN, width=340)

    async def do_login(_=None) -> None:
        if not username_f.value or not password_f.value:
            status_t.value   = "Please enter your username and password."
            status_t.visible = True
            page.update()          # ← update_async() deyil
            return

        login_btn.disabled = True
        progress.visible   = True
        status_t.visible   = False
        page.update()

        try:
            result = await APIClient().login(
                username_f.value.strip(), password_f.value
            )
            page.session.set("token",    result["access_token"])
            page.session.set("username", username_f.value.strip())
            await page.push_route("/dashboard")   # ← go_async() deyil
        except APIError as exc:
            status_t.value   = exc.message
            status_t.visible = True
        finally:
            login_btn.disabled = False
            progress.visible   = False
            page.update()

    login_btn.on_click   = do_login
    username_f.on_submit = do_login
    password_f.on_submit = do_login

    async def go_signup(_=None) -> None:
        await page.push_route("/signup")   # ← go_async() deyil

    card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.FLIGHT_TAKEOFF, size=56, color=ft.Colors.BLUE_400),
                ft.Text("Drone Dispatch Portal", size=26, weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER),
                ft.Text("Sign in to manage your fleet", size=14,
                        color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                ft.Container(height=4),
                username_f,
                password_f,
                status_t,
                progress,
                ft.Container(height=2),
                login_btn,
                ft.Row(
                    [
                        ft.Text("No account yet?", size=13, color=ft.Colors.GREY_500),
                        ft.TextButton("Create one", on_click=go_signup),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
        padding=ft.padding.all(42),
        width=430,
    )

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                content=ft.Card(content=card, elevation=10),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )