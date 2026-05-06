"""Application entry-point and router."""
from __future__ import annotations

# ── path fix ──────────────────────────────────────────────────────────────────
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# ─────────────────────────────────────────────────────────────────────────────

import flet as ft
import ui.state as state

from ui.views.login_view import build_login_view
from ui.views.signup_view import build_signup_view
from ui.views.dashboard.shell import build_dashboard_shell


async def main(page: ft.Page) -> None:
    page.title = "Drone Dispatch — Management Portal"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.window.width = 480
    page.window.height = 860
    page.window.min_width = 400
    page.window.min_height = 700
    page.padding = 0
    page.window.update()

    async def route_change(e) -> None:
        page.views.clear()

        logged_in: bool = state.get("logged_in") is True

        if page.route == "/signup":
            page.views.append(build_signup_view(page))

        elif page.route == "/dashboard" and logged_in:
            shell_view, init_fn = build_dashboard_shell(page)
            page.views.append(shell_view)
            page.update()
            await init_fn()
            return

        else:
            page.views.append(build_login_view(page))

        page.update()

    async def view_pop(e) -> None:
        if len(page.views) > 1:
            page.views.pop()
        top = page.views[-1]
        await page.push_route(top.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await page.push_route("/login")


if __name__ == "__main__":
    ft.run(main)
