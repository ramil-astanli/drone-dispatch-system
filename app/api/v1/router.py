from fastapi import APIRouter

from app.api.v1.endpoints import auth, customers, dispatch, drones, packages, routes

api_router = APIRouter()

# Public
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Protected (individual endpoints carry the get_current_user dependency)
api_router.include_router(drones.router, prefix="/drones", tags=["Drones"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(packages.router, prefix="/packages", tags=["Packages"])
api_router.include_router(routes.router, prefix="/routes", tags=["Routes"])
api_router.include_router(dispatch.router, prefix="/dispatch", tags=["Dispatch"])
