
-- load table toponyms_types : types of toponyms in breton and in french
INSERT INTO toponyms_types (type_br, type_fr) VALUES
    ('Beg', 'Pointe'),
    ('Bro', 'Pays'),
    ('Departamant', 'Département'),
    ('Diseurt', 'Divers'),
    ('Dour', 'Eau'),
    ('Enez', 'Île'),
    ('Etrekumuniezh', 'Intercommunalité'),
    ('Hent', 'Chemin'),
    ('Karreg', 'Pierre'),
    ('Karter', 'Quartier'),
    ('Koad', 'Bois'),
    ('Kumun', 'Commune'),
    ('Kumun dileuriet', 'Commune déléguée'),
    ('Kumun gozh', 'Commune historique'),
    ('Kumun mod nevez', 'Commune nouvelle'),
    ('Kêriadenn', 'Village'),
    ('Maez', 'Champ'),
    ('Monumant/Savadur', 'Monument/Bâtiment'),
    ('Porzh(-mor)', 'Port'),
    ('Rann (eus ar gumun)', 'Partie (de la commune)'),
    ('Takad', 'Superficie'),
    ('Uhelenn', 'Point haut');



-- load table municipalities from the kerofis table : the places of type Kumun, with the number of toponyms of the municipality
-- (same content as the former view municipalities)
INSERT INTO municipalities
SELECT
    k.insee,
    k.kumun AS name_br,
    k.stumm_orin AS name_fr,
    n.nb_toponyms
FROM kerofis k
    JOIN (SELECT insee, count(*) AS nb_toponyms FROM kerofis GROUP BY insee) n ON n.insee = k.insee
WHERE k.rummad = 'Kumun'
ORDER BY k.insee;


-- load table toponyms from the kerofis table
INSERT INTO toponyms
SELECT
    niv AS id,
    insee,
    rummad AS type_br,
    stumm_dibab AS name_br,
    t.type_fr,
    stumm_orin AS name_fr
FROM kerofis k
	JOIN toponyms_types t ON k.rummad = t.type_br
ORDER BY insee, name_br;


-- load table infos with version of KerOfis database
INSERT INTO infos
	SELECT
		'kerofis_version' AS key,
		deiziad_restr AS value
	FROM kerofis
	LIMIT 1;

-- date of import
INSERT INTO infos
	SELECT
		'import_date' AS key,
		date('now','localtime') AS value
;

-- number of municipalities
INSERT INTO infos
	SELECT
		'municipalities_count' AS key,
		count(*) AS value
	FROM municipalities
;

-- number of toponyms
INSERT INTO infos
	SELECT
		'toponyms_count' AS key,
		count(*) AS value
	FROM toponyms
;


