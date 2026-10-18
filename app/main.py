"""KerOfis API : FastAPI application."""
import sqlite3
from pathlib import Path

from typing import Annotated, Literal

from fastapi import APIRouter, FastAPI, HTTPException, Query

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


def query_db(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Run a read-only query on the KerOfis database."""
    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute(sql, params).fetchall()
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


def get_municipality_infos(insee: str) -> dict | None:
    """General information about a municipality, None if the code is not a municipality."""
    rows = query_db(
        "SELECT insee, name_br, name_fr, nb_toponyms FROM municipality WHERE insee = ?",
        (insee,),
    )
    return dict(rows[0]) if rows else None


def get_municipality_statistics(insee: str) -> list[dict]:
    """Number of toponyms per type for a municipality."""
    rows = query_db(
        "SELECT insee, rummad, nb FROM stats_municipality_type_of_toponyms WHERE insee = ?",
        (insee,),
    )
    return [dict(row) for row in rows]


def get_municipality_toponyms(insee: str) -> list[dict]:
    """All the toponyms of a municipality, sorted by name."""
    rows = query_db(
        "SELECT niv, deiziad_degemer, insee, kumun, stagadenn, lec_hanv, stumm_orin, rummad, stumm_dibab "
        "FROM kerofis WHERE insee = ? ORDER BY lec_hanv",
        (insee,),
    )
    return [dict(row) for row in rows]


def not_found(insee: str) -> HTTPException:
    return HTTPException(status_code=404, detail=f"No toponym for INSEE code {insee}")


@router.get("/municipality/{insee}/")
def municipality(insee: str) -> dict:
    """Infos, statistics and all the toponyms of one municipality, from its INSEE code."""
    toponyms = get_municipality_toponyms(insee)
    if not toponyms:
        raise not_found(insee)

    return {
        "infos": get_municipality_infos(insee),
        "statistics": get_municipality_statistics(insee),
        "toponyms": toponyms,
    }


@router.get("/municipality/{insee}/infos/")
def municipality_infos(insee: str) -> dict:
    """General information about one municipality : INSEE code, names and number of toponyms."""
    infos = get_municipality_infos(insee)
    if infos is None:
        raise not_found(insee)
    return infos


@router.get("/municipality/{insee}/statistics/")
def municipality_statistics(insee: str) -> list[dict]:
    """Number of toponyms per type for one municipality."""
    statistics = get_municipality_statistics(insee)
    if not statistics:
        raise not_found(insee)
    return statistics


@router.get("/municipality/{insee}/toponyms/")
def municipality_toponyms(insee: str) -> list[dict]:
    """All the toponyms of one municipality."""
    toponyms = get_municipality_toponyms(insee)
    if not toponyms:
        raise not_found(insee)
    return toponyms


def like_pattern(text: str, prefix_only: bool = False) -> str:
    """LIKE pattern matching a text, with the LIKE wildcards of the text escaped (ESCAPE '\\')."""
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"{escaped}%" if prefix_only else f"%{escaped}%"


# search criteria must have at least 2 characters
SearchText = Annotated[str | None, Query(min_length=2)]


@router.get("/search/municipalities/")
def search_municipalities(
    insee: SearchText = None,
    name_br: SearchText = None,
    name_fr: SearchText = None,
    sort: Literal["insee", "name_br", "name_fr"] = "name_br",
) -> dict:
    """Search municipalities. At least one criterion is required, several are combined (AND).

    - insee : the INSEE code starts with the value (`29` : the whole department)
    - name_br : the breton name contains the value
    - name_fr : the french name contains the value
    - sort : the sort criterion : insee, name_br or name_fr (default : name_br)

    The response gives the number of municipalities found, then the list of the municipalities.
    """
    conditions = []
    params = []
    if insee is not None:
        conditions.append("insee LIKE ? ESCAPE '\\'")
        params.append(like_pattern(insee, prefix_only=True))
    if name_br is not None:
        conditions.append("name_br LIKE ? ESCAPE '\\'")
        params.append(like_pattern(name_br))
    if name_fr is not None:
        conditions.append("name_fr LIKE ? ESCAPE '\\'")
        params.append(like_pattern(name_fr))
    if not conditions:
        raise HTTPException(
            status_code=422, detail="At least one search criterion is required : insee, name_br or name_fr"
        )

    rows = query_db(
        "SELECT insee, name_br, name_fr, nb_toponyms FROM municipality WHERE "
        + " AND ".join(conditions)
        + f" ORDER BY {sort} COLLATE NOCASE, insee",
        tuple(params),
    )
    municipalities = [dict(row) for row in rows]
    return {"count": len(municipalities), "municipalities": municipalities}


app.include_router(router)
