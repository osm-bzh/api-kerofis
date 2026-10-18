-- SQLite3 version of setup/create_views.sql (PostgreSQL)
-- No CREATE OR REPLACE VIEW in SQLite : DROP VIEW IF EXISTS then CREATE VIEW.
-- No OWNER in SQLite.
-- Views are dropped in reverse dependency order, and created in dependency order.

DROP VIEW IF EXISTS stats_municipality;
DROP VIEW IF EXISTS stats_municipality_name_br;
DROP VIEW IF EXISTS municipalities;
DROP VIEW IF EXISTS infos_file_import;
DROP VIEW IF EXISTS stats_municipality_type_of_place;
DROP VIEW IF EXISTS stats_type_of_place;


-- this view get the number of items per date of import version
-- of the original data file

CREATE VIEW infos_file_import AS
 SELECT kerofis.deiziad_restr,
    count(kerofis.deiziad_restr) AS nb
   FROM kerofis
  GROUP BY kerofis.deiziad_restr
  ORDER BY kerofis.deiziad_restr DESC;


-- this view to list all the municipality
-- id, breton name, french name

CREATE VIEW municipalities AS
 SELECT kerofis.insee,
    kerofis.kumun AS name_br,
    kerofis.stumm_orin AS name_fr,
    nb.nb_toponyms
   FROM kerofis
     LEFT JOIN ( SELECT kerofis.insee,
            count(*) AS nb_toponyms
           FROM kerofis
          GROUP BY kerofis.insee) nb ON nb.insee = kerofis.insee
  WHERE kerofis.rummad = 'Kumun'
  ORDER BY kerofis.insee;


-- this view to get the number of name:br occurences per municipality
-- without names of the municipality

CREATE VIEW stats_municipality_name_br AS
 SELECT kerofis.insee,
    count(*) AS nb
   FROM kerofis
  GROUP BY kerofis.insee
  ORDER BY kerofis.insee;


-- this view to get statistics on the type of toponyms per municipality

CREATE VIEW stats_municipality_type_of_toponyms AS
    SELECT
        kerofis.insee,
        kerofis.rummad,
      count(kerofis.rummad) AS nb
    FROM kerofis
    GROUP BY
        kerofis.insee,
        kerofis.rummad
;


-- this view for global statistics on type of places

CREATE VIEW stats_type_of_place AS
 SELECT kerofis.rummad,
    count(kerofis.rummad) AS nb
   FROM kerofis
  GROUP BY kerofis.rummad
  ORDER BY kerofis.rummad;
