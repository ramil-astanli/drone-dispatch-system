"""Signup screen."""
from __future__ import annotations

import flet as ft

from ui.api.client import APIClient, APIError
from ui.utils import field


def build_signup_view(page: ft.Page) -> ft.View:
    username_f = field("Username", prefix_icon=ft.Icons.PERSON_OUTLINE,
                       autofocus=True, width=340)
    email_f    = field("Email", prefix_icon=ft.Icons.EMAIL_OUTLINED,
                       keyboard_type=ft.KeyboardType.EMAIL, width=340)
    password_f = field("Password (min 8 chars)", prefix_icon=ft.Icons.LOCK_OUTLINE,
                       password=True, can_reveal_password=True, width=340)
    status_t   = ft.Text("", color=ft.Colors.RED_400, size=13, visible=False)
    progress   = ft.ProgressBar(visible=False, width=340, color=ft.Colors.BLUE_400)
    signup_btn = ft.FilledButton("Create Account", icon=ft.Icons.PERSON_ADD, width=340)

    async def do_signup(_=None) -> None:
        for f in (username_f, email_f, password_f):
            f.error_text = None

        errors = False
        if not username_f.value or len(username_f.value.strip()) < 3:
            username_f.error_text = "At least 3 characters required."
            errors = True
        if not email_f.value or "@" not in email_f.value:
            email_f.error_text = "Enter a valid email address."
            errors = True
        if not password_f.value or len(password_f.value) < 8:
            password_f.error_text = "Password must be at least 8 characters."
            errors = True

        if errors:
            page.update()
            return

        signup_btn.disabled = True
        progress.visible    = True
        status_t.visible    = False
        page.update()

        try:
            await APIClient().signup(
                username_f.value.strip(),
                email_f.value.strip(),
                password_f.value,
            )
            result = await APIClient().login(
                username_f.value.strip(), password_f.value
            )
            # FIX: .set() yoxdur, dict kimi istifadə et
            page.session["token"]    = result["access_token"]
            page.session["username"] = username_f.value.strip()
            await page.push_route("/dashboard")
        except APIError as exc:
            status_t.value   = exc.message
            status_t.visible = True
        finally:
            signup_btn.disabled = False
            progress.visible    = False
            page.update()

    signup_btn.on_click = do_signup

    async def go_login(_=None) -> None:
        await page.push_route("/login")

    card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.FLIGHT_TAKEOFF, size=56, color=ft.Colors.BLUE_400),
                ft.Text("Create an Account", size=26, weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER),
                ft.Text("Join the Drone Dispatch Portal", size=14,
                        color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                ft.Container(height=4),
                username_f,
                email_f,
                password_f,
                status_t,
                progress,
                ft.Container(height=2),
                signup_btn,
                ft.Row(
                    [
                        ft.Text("Already have an account?", size=13,
                                color=ft.Colors.GREY_500),
                        ft.TextButton("Sign in", on_click=go_login),
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
        route="/signup",
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