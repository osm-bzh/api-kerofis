-- SQLite3 version of setup/create_database.sql (PostgreSQL)
-- Not applicable in SQLite: CREATE USER, CREATE DATABASE, OWNER, schema "public".
-- The database is simply the file opened with : sqlite3 kerofis.db < create_tables.sql

-- main table
-- dates are stored as ISO 8601 text (YYYY-MM-DD), SQLite has no native date type

DROP TABLE IF EXISTS kerofis;
CREATE TABLE kerofis (
    niv             INTEGER NOT NULL,
    deiziad_degemer TEXT,
    insee           TEXT,
    kumun           TEXT,
    stagadenn       TEXT,
    lec_hanv        TEXT,
    stumm_orin      TEXT,
    rummad          TEXT,
    stumm_dibab     TEXT,
    deiziad_restr   TEXT,
    CONSTRAINT pk_niv PRIMARY KEY (niv)
);

CREATE INDEX idx_insee ON kerofis (insee);
CREATE INDEX idx_stumm_didab ON kerofis (stumm_dibab);
CREATE INDEX idx_stumm_orin ON kerofis (stumm_orin);
