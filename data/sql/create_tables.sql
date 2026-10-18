-- SQLite3 version of setup/create_database.sql (PostgreSQL)
-- Not applicable in SQLite: CREATE USER, CREATE DATABASE, OWNER, schema "public".
-- The database is simply the file opened with : sqlite3 kerofis.db < create_tables.sql

-- data source table
-- data are loaded from CSV
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

-- the toponyms
DROP TABLE IF EXISTS toponyms;
CREATE TABLE toponyms (
    id             INTEGER NOT NULL,
    insee          TEXT NULL,
    type_br        TEXT NULL,
    name_br        TEXT NULL,
    type_fr        TEXT NULL,
    name_fr        TEXT NULL,
    CONSTRAINT pk_id PRIMARY KEY (id)
);

CREATE INDEX idx_toponyms_insee   ON toponyms (insee);
CREATE INDEX idx_toponyms_type_br ON toponyms (type_br);
CREATE INDEX idx_toponyms_name_br ON toponyms (name_br);
CREATE INDEX idx_toponyms_type_fr ON toponyms (type_fr);
CREATE INDEX idx_toponyms_name_fr ON toponyms (name_fr);

