
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


