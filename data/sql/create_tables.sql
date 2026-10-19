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


-- the municipalities : INSEE code, breton name, french name and number of toponyms
-- no primary key on insee : some codes (98888, 99999...) are shared by several places which are not municipalities
DROP TABLE IF EXISTS municipalities;
CREATE TABLE municipalities (
    insee          TEXT NOT NULL,
    name_br        TEXT NULL,
    name_fr        TEXT NULL,
    nb_toponyms    INTEGER NOT NULL
);

CREATE INDEX idx_municipalities_insee   ON municipalities (insee);
CREATE INDEX idx_municipalities_name_br ON municipalities (name_br);
CREATE INDEX idx_municipalities_name_fr ON municipalities (name_fr);


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


-- toponyms types
DROP TABLE IF EXISTS toponyms_types;
CREATE TABLE toponyms_types (
    type_br        TEXT NOT NULL,
    type_fr        TEXT NOT NULL
);

CREATE INDEX idx_toponyms_types_type_br ON toponyms (type_br);
CREATE INDEX idx_toponyms_types_type_fr ON toponyms (type_fr);

