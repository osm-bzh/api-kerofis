"""KerOfis API : FastAPI application."""
import sqlite3
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException

# the API is served under http://localhost/api-kerofis/
API_PREFIX = "/api-kerofis"

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "kerofis.db"

app = FastAPI(
    title="API KerOfis",
    docs_url=f"{API_PREFIX}/docs/",
    redoc_url=f"{API_PREFIX}/redoc/",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

router = APIRouter(prefix=API_PREFIX)


@router.get("/")
def index() -> dict:
    return {"name": "API KerOfis"}


def query_db(sql: str) -> list[sqlite3.Row]:
    """Run a read-only query on the KerOfis database."""
    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(sql).fetchall()
    except sqlite3.Error as error:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {error}")


@router.get("/infos/")
def infos() -> dict:
    """General information about the data : licence, attribution and version of the data file."""
    # the view is sorted by import date, most recent first
    rows = query_db("SELECT deiziad_restr FROM infos_file_import LIMIT 1")
    if not rows:
        raise HTTPException(status_code=503, detail="Database is empty")

    return {
        "attribution_br": "KerOfis gant osm-bzh",
        "attribution_en": "KerOfis by osm-bzh",
        "attribution_fr": "KerOfis par osm-bzh",
        "version_kerofis": rows[0]["deiziad_restr"],
        "licence": "Open Database License (ODbL) v1.0",
        "name": "KerOfis data provided by Ofis publik ar brezhoneg",
    }


@router.get("/municipalities/")
def municipalities() -> list[dict]:
    """List of all the municipalities : INSEE code, breton name and french name."""
    rows = query_db("SELECT insee, name_br, name_fr, nb_toponyms FROM municipality")
    return [dict(row) for row in rows]


app.include_router(router)
