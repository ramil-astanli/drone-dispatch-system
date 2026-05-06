"""Async HTTP client for the Spring Boot backend."""
from __future__ import annotations

import httpx

BASE_URL = "http://localhost:8000/api/v1"
_TIMEOUT = 15.0


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def __str__(self) -> str:
        return self.message


class APIClient:
    """Thin async wrapper around httpx."""

    def __init__(self, token: str | None = None) -> None:
        # Token kept for forward-compat; unused when JWT is disabled.
        self._token = token

    # ── private helpers ───────────────────────────────────────────────────────

    def _headers(self, extra: dict | None = None) -> dict[str, str]:
        h: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        if extra:
            h.update(extra)
        return h

    async def _check(self, resp: httpx.Response) -> None:
        if resp.status_code in (200, 201, 204):
            return
        try:
            detail = resp.json().get("detail") or resp.json().get("message") or resp.text
        except Exception:
            detail = resp.text

        match resp.status_code:
            case 401:
                raise APIError("Invalid credentials — please try again.", 401)
            case 403:
                raise APIError("Access denied.", 403)
            case 404:
                raise APIError(str(detail), 404)
            case 409:
                raise APIError(str(detail), 409)
            case 422:
                raise APIError(f"Validation error: {detail}", 422)
            case _:
                raise APIError(f"Server error {resp.status_code}: {detail}", resp.status_code)

    # ── auth endpoints ────────────────────────────────────────────────────────

    async def login(self, username: str, password: str) -> dict:
        """POST credentials as OAuth2 form data (required by OAuth2PasswordRequestForm)."""
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
                r = await c.post(
                    f"{BASE_URL}/auth/login",
                    data={"username": username, "password": password, "grant_type": "password"},
                )
                await self._check(r)
                try:
                    return r.json()
                except Exception:
                    return {}          # 200 with no body is fine
        except httpx.RequestError as exc:
            raise APIError(f"Cannot reach server: {exc}")

    async def signup(self, username: str, email: str, password: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
                r = await c.post(
                    f"{BASE_URL}/auth/signup",
                    json={"username": username, "email": email, "password": password},
                )
                await self._check(r)
                try:
                    return r.json()
                except Exception:
                    return {}
        except httpx.RequestError as exc:
            raise APIError(f"Cannot reach server: {exc}")

    # ── CRUD helpers ──────────────────────────────────────────────────────────

    async def get(self, path: str) -> list | dict:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
                r = await c.get(f"{BASE_URL}{path}", headers=self._headers())
                await self._check(r)
                return r.json()
        except httpx.RequestError as exc:
            raise APIError(f"Cannot reach server: {exc}")

    async def post(self, path: str, json: dict | None = None) -> dict:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
                r = await c.post(f"{BASE_URL}{path}", json=json, headers=self._headers())
                await self._check(r)
                try:
                    return r.json()
                except Exception:
                    return {}
        except httpx.RequestError as exc:
            raise APIError(f"Cannot reach server: {exc}")

    async def patch(self, path: str, json: dict | None = None) -> dict:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
                r = await c.patch(f"{BASE_URL}{path}", json=json, headers=self._headers())
                await self._check(r)
                try:
                    return r.json()
                except Exception:
                    return {}
        except httpx.RequestError as exc:
            raise APIError(f"Cannot reach server: {exc}")

    async def delete(self, path: str) -> None:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as c:
                r = await c.delete(f"{BASE_URL}{path}", headers=self._headers())
                if r.status_code == 204:
                    return
                await self._check(r)
        except httpx.RequestError as exc:
            raise APIError(f"Cannot reach server: {exc}")
