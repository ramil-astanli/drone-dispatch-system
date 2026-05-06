"""Shared UI primitives — badges, widgets, snackbar helper."""
from __future__ import annotations

import flet as ft

# ── Status / priority colour palette ─────────────────────────────────────────
# (background_hex, text_hex)
_PALETTE: dict[str, tuple[str, str]] = {
    # Drone statuses
    "IDLE":        ("#C8E6C9", "#1B5E20"),
    "LOADING":     ("#FFE0B2", "#E65100"),
    "DELIVERING":  ("#BBDEFB", "#0D47A1"),
    "DELIVERED":   ("#B2DFDB", "#004D40"),
    "RETURNING":   ("#E1BEE7", "#4A148C"),
    "CHARGING":    ("#FFF9C4", "#F57F17"),
    # Route statuses
    "PENDING":     ("#FFE0B2", "#E65100"),
    "IN_PROGRESS": ("#BBDEFB", "#0D47A1"),
    "COMPLETED":   ("#C8E6C9", "#1B5E20"),
    "CANCELLED":   ("#FFCDD2", "#B71C1C"),
    # Package priority
    "LOW":         ("#ECEFF1", "#37474F"),
    "MEDIUM":      ("#E3F2FD", "#1565C0"),
    "HIGH":        ("#FFCDD2", "#C62828"),
}


def status_badge(label: str) -> ft.Container:
    bg, fg = _PALETTE.get(label, ("#ECEFF1", "#37474F"))
    return ft.Container(
        content=ft.Text(label, size=11, weight=ft.FontWeight.W_600, color=fg),
        bgcolor=bg,
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=10, vertical=3),
    )


def battery_widget(level: int) -> ft.Row:
    if level > 75:
        color, icon = ft.Colors.GREEN_400, ft.Icons.BATTERY_FULL
    elif level > 50:
        color, icon = ft.Colors.LIGHT_GREEN_400, ft.Icons.BATTERY_5_BAR
    elif level > 25:
        color, icon = ft.Colors.ORANGE_400, ft.Icons.BATTERY_3_BAR
    else:
        color, icon = ft.Colors.RED_400, ft.Icons.BATTERY_1_BAR
    return ft.Row(
        [
            ft.Icon(icon, color=color, size=16),
            ft.Text(f"{level}%", color=color, weight=ft.FontWeight.W_600, size=13),
        ],
        spacing=4,
        tight=True,
    )


def stat_card(icon: str, label: str, value: str, color: str) -> ft.Card:
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [ft.Icon(icon, color=color, size=28),
                         ft.Text(label, size=13, color=ft.Colors.GREY_500)],
                        spacing=8,
                    ),
                    ft.Text(value, size=38, weight=ft.FontWeight.BOLD),
                ],
                spacing=6,
            ),
            padding=ft.Padding.all(22),
            width=190,
        ),
        elevation=3,
    )


def section_header(title: str, subtitle: str | None = None) -> ft.Column:
    controls: list[ft.Control] = [
        ft.Text(title, size=24, weight=ft.FontWeight.BOLD)
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=13, color=ft.Colors.GREY_500))
    return ft.Column(controls, spacing=2)


def loading_center() -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [ft.ProgressRing(width=42, height=42, stroke_width=4)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )


def error_card(message: str) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_400, size=22),
                ft.Text(message, color=ft.Colors.RED_300, expand=True),
            ],
            spacing=10,
        ),
        bgcolor="#2D1B1B",
        border=ft.border.all(1, ft.Colors.RED_900),
        border_radius=8,
        padding=ft.Padding.all(14),
    )


def show_snack(page: ft.Page, message: str, *, error: bool = False) -> None:
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_800 if error else ft.Colors.GREEN_700,
        duration=3500,
    )
    page.snack_bar.open = True


def field(label: str, **kwargs) -> ft.TextField:
    return ft.TextField(label=label, border_radius=8, **kwargs)
