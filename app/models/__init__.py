# Import every model here so that Base.metadata is fully populated
# before create_all() is called during application startup.
from app.core.database import Base
from app.models.customer import Customer
from app.models.drone import Drone, DroneModel, DroneStatus
from app.models.package import Package, PackagePriority
from app.models.route import Route, RouteStatus
from app.models.user import User

__all__ = [
    "Base",
    "Customer",
    "Drone",
    "DroneModel",
    "DroneStatus",
    "Package",
    "PackagePriority",
    "Route",
    "RouteStatus",
    "User",
]
