from fastapi import HTTPException, status

# ── Auth ──────────────────────────────────────────────────────────────────────

class InvalidTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )


class UsernameAlreadyTakenError(HTTPException):
    def __init__(self, username: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The username '{username}' is already taken.",
        )


# ── Domain ────────────────────────────────────────────────────────────────────

class DroneNotFoundError(HTTPException):
    def __init__(self, drone_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drone with id={drone_id} not found.",
        )


class PackageNotFoundError(HTTPException):
    def __init__(self, package_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Package with id={package_id} not found.",
        )


class NoDronesAvailableError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="No available drones found. All drones are busy or below the minimum battery threshold.",
        )


class CustomerNotFoundError(HTTPException):
    def __init__(self, customer_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id={customer_id} not found.",
        )


class EmailAlreadyRegisteredError(HTTPException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The email '{email}' is already registered.",
        )


class PackageAlreadyDispatchedError(HTTPException):
    def __init__(self, package_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Package with id={package_id} has already been dispatched.",
        )
