"""Application entry-point and router."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import flet as ft

try:
    from ui.views.login_view import build_login_view
    from ui.views.signup_view import build_signup_view
    from ui.views.dashboard.shell import build_dashboard_shell
except ImportError as e:
    print(f"Import Xətası: {e}. 'ui' qovluğunda __init__.py olduğundan əmin ol.")


def get_token(page: ft.Page) -> str | None:
    """Session-dan token-i təhlükəsiz oxu."""
    try:
        return page.session.get("token")
    except Exception:
        pass
    try:
        return page.session["token"]
    except Exception:
        return None


async def main(page: ft.Page) -> None:
    page.title = "Drone Dispatch — Management Portal"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)

    page.window.width = 1280
    page.window.height = 800
    page.padding = 0

    async def route_change(e) -> None:
        page.views.clear()

        token = get_token(page)

        if page.route == "/signup":
            page.views.append(build_signup_view(page))

        elif not token or page.route in ("/", "/login"):
            page.views.append(build_login_view(page))

        else:
            shell_view, init_fn = build_dashboard_shell(page)
            page.views.append(shell_view)
            if init_fn:
                await init_fn()

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