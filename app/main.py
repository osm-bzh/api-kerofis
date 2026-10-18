"""KerOfis API : FastAPI application."""
import argparse
import os
import sqlite3
import sys
import unicodedata
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, FastAPI, HTTPException, Query

# the API is served under http://localhost/api-kerofis/
API_PREFIX = "/api-kerofis"

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "kerofis.db"

# print the SQL queries sent to the database : python -m app.main --debug-sql
# (or KEROFIS_DEBUG_SQL=1 when the application is started directly with uvicorn)
DEBUG_SQL_ENV = "KEROFIS_DEBUG_SQL"

app = FastAPI(
    title="API KerOfis by OSM-Bzh",
    docs_url=f"{API_PREFIX}/docs/",
    redoc_url=f"{API_PREFIX}/redoc/",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

router = APIRouter(prefix=API_PREFIX)


@router.get("/")
def index() -> dict:
    return {"name": "API KerOfis by OSM-Bzh"}


def normalize(text: str | None) -> str | None:
    """Lower case and remove the accents of a text : `Kêriadenn` -> `keriadenn`."""
    if text is None:
        return None
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def query_db(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Run a read-only query on the KerOfis database. The SQL function normalize() is available."""
    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            conn.create_function("normalize", 1, normalize, deterministic=True)
            if os.environ.get(DEBUG_SQL_ENV) == "1":
                # the callback gets the statement with its parameters already replaced
                conn.set_trace_callback(lambda statement: print(f"[SQL] {statement}", file=sys.stderr, flush=True))
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
    rows = query_db("SELECT insee, name_br, name_fr, nb_toponyms FROM municipalities")
    return [dict(row) for row in rows]


def get_municipality_infos(insee: str) -> dict | None:
    """General information about a municipality, None if the code is not a municipality."""
    rows = query_db(
        "SELECT insee, name_br, name_fr, nb_toponyms FROM municipalities WHERE insee = ?",
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


def add_like_condition(
    conditions: list[str], params: list, column: str, value: str | None, prefix_only: bool = False
) -> None:
    """Add a LIKE condition on a column to a search, if the criterion is given."""
    if value is not None:
        conditions.append(f"{column} LIKE ? ESCAPE '\\'")
        params.append(like_pattern(value, prefix_only))


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
    add_like_condition(conditions, params, "insee", insee, prefix_only=True)
    add_like_condition(conditions, params, "name_br", name_br)
    add_like_condition(conditions, params, "name_fr", name_fr)
    if not conditions:
        raise HTTPException(
            status_code=422, detail="At least one search criterion is required : insee, name_br or name_fr"
        )

    rows = query_db(
        "SELECT insee, name_br, name_fr, nb_toponyms FROM municipalities WHERE "
        + " AND ".join(conditions)
        + f" ORDER BY {sort} COLLATE NOCASE, insee",
        tuple(params),
    )
    municipalities = [dict(row) for row in rows]
    return {"count": len(municipalities), "municipalities": municipalities}


# columns of the kerofis table used to sort the toponyms
TOPONYM_SORT_COLUMNS = {"insee": "insee", "name_br": "stumm_dibab", "name_fr": "stumm_orin"}


@router.get("/search/toponyms/")
def search_toponyms(
    insee: SearchText = None,
    name_br: SearchText = None,
    name_fr: SearchText = None,
    type: SearchText = None,
    sort: Literal["insee", "name_br", "name_fr"] = "name_br",
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    """Search toponyms. At least one criterion is required, several are combined (AND).

    - insee : the INSEE code starts with the value (`29` : the whole department)
    - name_br : the breton name contains the value
    - name_fr : the french name contains the value
    - type : the type of toponym is the value, in lower case without accents (`keriadenn`)
    - sort : the sort criterion : insee, name_br or name_fr (default : name_br)
    - limit, offset : pagination (default : 100 toponyms from the first one, 1000 at most)

    The response gives the total number of toponyms found (whatever the pagination),
    then the list of the toponyms of the requested page.
    """
    conditions = []
    params = []
    add_like_condition(conditions, params, "insee", insee, prefix_only=True)
    add_like_condition(conditions, params, "stumm_dibab", name_br)
    add_like_condition(conditions, params, "stumm_orin", name_fr)
    if type is not None:
        conditions.append("normalize(rummad) = ?")
        params.append(normalize(type))
    if not conditions:
        raise HTTPException(
            status_code=422, detail="At least one search criterion is required : insee, name_br, name_fr or type"
        )

    where = " AND ".join(conditions)
    count = query_db(f"SELECT count(*) FROM kerofis WHERE {where}", tuple(params))[0][0]
    rows = query_db(
        "SELECT niv, deiziad_degemer, insee, kumun, stagadenn, lec_hanv, stumm_orin, rummad, stumm_dibab "
        f"FROM kerofis WHERE {where} "
        f"ORDER BY {TOPONYM_SORT_COLUMNS[sort]} COLLATE NOCASE, niv LIMIT ? OFFSET ?",
        (*params, limit, offset),
    )
    return {"count": count, "toponyms": [dict(row) for row in rows]}


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Start the KerOfis API.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="restart the server when the code changes")
    parser.add_argument("--debug-sql", action="store_true", help="print the SQL queries in the console")
    args = parser.parse_args()

    if args.debug_sql:
        # an environment variable is inherited by the process restarted by --reload
        os.environ[DEBUG_SQL_ENV] = "1"
    uvicorn.run("app.main:app", port=args.port, reload=args.reload)
