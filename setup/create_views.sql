

-- View: v_infos_deiziad_restr

-- DROP VIEW v_infos_deiziad_restr;

CREATE OR REPLACE VIEW v_infos_deiziad_restr AS 
 SELECT kerofis.deiziad_restr,
    count(kerofis.deiziad_restr) AS nb
   FROM kerofis
  GROUP BY kerofis.deiziad_restr
  ORDER BY kerofis.deiziad_restr DESC;



-- View: v_kumun_listenn

-- DROP VIEW v_kumun_listenn;

CREATE OR REPLACE VIEW v_kumun_listenn AS 
 SELECT kerofis.insee,
    kerofis.kumun AS name_br,
    kerofis.stumm_orin AS name_fr
   FROM kerofis
  WHERE kerofis.rummad::text = 'Kumun'::text
  ORDER BY kerofis.insee;


-- View: v_kumun_nb

-- DROP VIEW v_kumun_nb;

CREATE OR REPLACE VIEW v_kumun_nb AS 
 SELECT kerofis.insee,
    count(*) AS nb
   FROM kerofis
  GROUP BY kerofis.insee
  ORDER BY kerofis.insee;


-- View: v_stats_kumun

-- DROP VIEW v_stats_kumun;

CREATE OR REPLACE VIEW v_stats_kumun AS 
 SELECT v_kumun_listenn.insee,
    v_kumun_listenn.name_br,
    v_kumun_listenn.name_fr,
    v_kumun_nb.nb
   FROM v_kumun_listenn,
    v_kumun_nb
  WHERE v_kumun_listenn.insee::text = v_kumun_nb.insee::text;



-- View: v_stats_kumun_rummad

-- DROP VIEW v_stats_kumun_rummad;

CREATE OR REPLACE VIEW v_stats_kumun_rummad AS 
 SELECT kerofis.insee,
    count(kerofis.rummad) AS nb,
    kerofis.rummad
   FROM kerofis
  GROUP BY kerofis.insee, kerofis.rummad
  ORDER BY kerofis.insee, count(kerofis.rummad) DESC;



-- View: v_stats_rummad

-- DROP VIEW v_stats_rummad;

CREATE OR REPLACE VIEW v_stats_rummad AS 
 SELECT kerofis.rummad,
    count(kerofis.rummad) AS nb
   FROM kerofis
  GROUP BY kerofis.rummad
  ORDER BY kerofis.rummad;

