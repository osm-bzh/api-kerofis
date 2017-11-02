

-- this view get the number of items per date of import version
-- of the original data file

-- DROP VIEW infos_file_import
CREATE OR REPLACE VIEW infos_file_import AS 
 SELECT kerofis.deiziad_restr,
    count(kerofis.deiziad_restr) AS nb
   FROM kerofis
  GROUP BY kerofis.deiziad_restr
  ORDER BY kerofis.deiziad_restr DESC;

ALTER TABLE infos_file_import OWNER TO kerofis;



-- this view to list all the municipality
-- id, breton name, french name

-- DROP VIEW municipality;
CREATE OR REPLACE VIEW municipality AS 
 SELECT kerofis.insee,
    kerofis.kumun AS name_br,
    kerofis.stumm_orin AS name_fr
   FROM kerofis
  WHERE kerofis.rummad::text = 'Kumun'::text
  ORDER BY kerofis.insee;

ALTER TABLE municipality OWNER TO kerofis;


-- this view to get the number of name:br occurences per municipality
-- without names of the municipality

-- DROP VIEW stats_municipality_name_br;
CREATE OR REPLACE VIEW stats_municipality_name_br AS 
 SELECT kerofis.insee,
    count(*) AS nb
   FROM kerofis
  GROUP BY kerofis.insee
  ORDER BY kerofis.insee;

ALTER TABLE stats_municipality_name_br OWNER TO kerofis;



-- municipality : names and number of name:br occurences

-- DROP VIEW stats_municipality;
CREATE OR REPLACE VIEW stats_municipality AS 
 SELECT municipality.insee,
    municipality.name_br,
    municipality.name_fr,
    stats_municipality_name_br.nb
   FROM municipality,
    stats_municipality_name_br
  WHERE municipality.insee::text = stats_municipality_name_br.insee::text;

ALTER TABLE stats_municipality OWNER TO kerofis;



-- this view to get statistics on the type of place per municipality

-- DROP VIEW stats_municipality_type_of_place;
CREATE OR REPLACE VIEW stats_municipality_type_of_place AS 
 SELECT kerofis.insee,
    count(kerofis.rummad) AS nb,
    kerofis.rummad
   FROM kerofis
  GROUP BY kerofis.insee, kerofis.rummad
  ORDER BY kerofis.insee, count(kerofis.rummad) DESC;

ALTER TABLE stats_municipality_type_of_place OWNER TO kerofis;



-- this view for global statistics on type of places

-- DROP VIEW stats_type_of_place;
CREATE OR REPLACE VIEW stats_type_of_place AS 
 SELECT kerofis.rummad,
    count(kerofis.rummad) AS nb
   FROM kerofis
  GROUP BY kerofis.rummad
  ORDER BY kerofis.rummad;

ALTER TABLE stats_type_of_place OWNER TO kerofis;


