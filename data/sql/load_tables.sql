
-- load table toponyms from the kerofis table
INSERT INTO toponyms
SELECT
    niv AS id,
    insee,
    rummad AS type_br,
    stumm_dibab AS name_br,
    NULL AS type_fr,
    stumm_orin AS name_fr
FROM kerofis
ORDER BY insee, name_br;

