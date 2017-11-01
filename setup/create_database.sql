
-- create a user
CREATE USER kerofis WITH PASSWORD 'kerofis';


-- create the database
CREATE DATABASE kerofis WITH OWNER=kerofis ENCODING=UTF8 ;


-- create the main table
CREATE TABLE public.kerofis (
    niv bigint NOT NULL,
    deiziad_degemer date,
    insee character varying(5),
    kumun character varying(250),
    stagadenn character varying(250),
    lec_hanv character varying(250),
    stumm_orin character varying(250),
    rummad character varying(50),
    stumm_dibab character varying(250),
    deiziad_restr date
);

ALTER TABLE public.kerofis
    ADD CONSTRAINT pk_niv PRIMARY KEY (niv);

CREATE INDEX idx_insee ON kerofis USING btree (insee);
CREATE INDEX idx_stumm_didab ON kerofis USING btree (stumm_dibab);
CREATE INDEX idx_stumm_orin ON kerofis USING btree (stumm_orin);


-- Add the postgres_fdw extension
-- to read a CSV file on the file system
-- https://wiki.postgresql.org/wiki/Foreign_data_wrappers

CREATE EXTENSION file_fdw ;

-- then setup a virtual table linked on the csv data file
CREATE SERVER kerofis_csv_import FOREIGN DATA WRAPPER file_fdw ; 

CREATE FOREIGN TABLE public.kerofis_csv_import
(
    stagadenn character varying(250),       -- stagadenn       / préfixe (FR)
    lec_hanv character varying(250),        -- lec_hanv        / nom (FR)
    kumun character varying(250),           -- kumun           / nom de la commune (BR)
    insee character varying(5),             -- insee           / code insee de la commune
    rummad character varying(50),           -- rummad          / type de toponyme (BR)
    dibab character varying(250),           -- stumm_dibab     / toponyme retenu (BR)
    deiziad_degemer character varying(10),  -- deiziad_degemer / date validation ou publication  0000-00-00 ou dd/mm/yyyy
    niv numeric(7,0)
)
SERVER kerofis_csv_import
OPTIONS (format 'csv', header 'true', delimiter ',', filename '/data/kerofis/kerofis_latest.csv');


-- load the main table from the import table
TRUNCATE TABLE public.kerofis ; 

INSERT INTO public.kerofis
(
  SELECT
    niv::bigint,
    (CASE
    WHEN deiziad_degemer = '0000-00-00' THEN '1970-01-01'
    -- french to english format '04/06/2013' -> '2013-06-04'
    ELSE CONCAT(SUBSTRING(deiziad_degemer,7,4),'-',SUBSTRING(deiziad_degemer,4,2),'-',SUBSTRING(deiziad_degemer,1,2))
    END)::date AS deiziad_degemer,
    insee,
    kumun,
    stagadenn,
    lec_hanv,
    (CASE
    -- when ends with single quote
    WHEN stagadenn LIKE '%''' THEN CONCAT(stagadenn,lec_hanv)
    ELSE CONCAT(stagadenn,' ',lec_hanv)
    END) AS stumm_orin,
    rummad,
    dibab AS stumm_dibab,
    '2017-10-31' AS deiziad_restr
  FROM kerofis_csv_import
);



