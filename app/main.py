"""KerOfis API : FastAPI application."""
import sqlite3
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException

# the API is served under http://localhost/api-kerofis/
API_PREFIX = "/api-kerofis"

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "kerofis.db"

app = FastAPI(title="API KerOfis")

router = APIRouter(prefix=API_PREFIX)


@router.get("/")
def index() -> dict:
    return {"name": "API KerOfis"}


@router.get("/infos/")
def infos() -> dict:
    """General information about the data : licence, attribution and version of the data file."""
    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
            # the view is sorted by import date, most recent first
            row = conn.execute("SELECT deiziad_restr FROM infos_file_import LIMIT 1").fetchone()
    except sqlite3.Error as error:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {error}")

    if row is None:
        raise HTTPException(status_code=503, detail="Database is empty")

    return {
        "attribution_br": "KerOfis gant osm-bzh",
        "attribution_en": "KerOfis by osm-bzh",
        "attribution_fr": "KerOfis par osm-bzh",
        "version_kerofis": row[0],
        "licence": "Open Database License (ODbL) v1.0",
        "name": "KerOfis data provided by Ofis publik ar brezhoneg",
    }


app.include_router(router)
