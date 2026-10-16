"""KerOfis API : FastAPI application."""
from fastapi import APIRouter, FastAPI

# the API is served under http://localhost/api-kerofis/
API_PREFIX = "/api-kerofis"

app = FastAPI(title="API KerOfis")

router = APIRouter(prefix=API_PREFIX)


@router.get("/")
def index() -> dict:
    return {"name": "API KerOfis"}


app.include_router(router)
