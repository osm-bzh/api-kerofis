-- SQLite3 version of setup/create_views.sql (PostgreSQL)
-- No CREATE OR REPLACE VIEW in SQLite : DROP VIEW IF EXISTS then CREATE VIEW.
-- No OWNER in SQLite.
-- Views are dropped in reverse dependency order, and created in dependency order.

DROP VIEW IF EXISTS stats_municipality;
DROP VIEW IF EXISTS stats_municipality_name_br;
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



-- this view to get statistics on the type of toponyms per municipality

CREATE VIEW stats_municipality_type_of_toponyms AS
    SELECT
        insee,
        type_br,
        type_fr,
    		count(type_br) AS count
    FROM toponyms
    GROUP BY insee, type_br ;


-- this view for global statistics on type of places

CREATE VIEW stats_type_of_place AS
	SELECT
	  type_br,
	  type_fr,
		count(type_br) AS count
	FROM toponyms
	GROUP BY type_br
	ORDER BY type_br;

