-- on vide
TRUNCATE kerofis ;

-- on charge
COPY kerofis (niv, deiziad_degemer, insee, kumun, stagadenn, lec_hanv, stumm_orin, rummad, stumm_dibab, deiziad_restr) 
FROM '/Users/mael/Documents/Projets/osm-br/KerOfis/org/kerofis_20160208_v2.csv' 
WITH CSV HEADER
