# CLAUDE.md

Contexte pour reprendre le projet avec Claude Code sur un autre ordinateur.

## Le projet

API FastAPI qui expose la toponymie bretonne KerOfis (Office public de la langue bretonne). Les données viennent d'exports CSV, chargés dans une base SQLite. Voir [README.md](README.md) pour la description complète, l'installation et les routes.

Le projet a été remis à zéro sur la branche `v2026.10` (commit « RAZ du projet »). L'ancien code (Flask, Python 2, PostgreSQL) reste sur `master` et **ne doit pas servir de base** : on repart d'une API neuve. On l'a seulement consulté pour reprendre les scripts SQL (`setup/create_database.sql`, `setup/create_views.sql`), déjà adaptés à SQLite.

## Organisation

- `app/main.py` : application FastAPI. Toutes les routes sont sous le préfixe `/api-kerofis` (constante `API_PREFIX`). L'accès à la base passe par `query_db()` (lecture seule).
- `scripts/load_csv_into_db.py` : recrée `data/kerofis.db` à partir du CSV le plus récent de `data/csv/` (date dans le nom `..._AAAAMMJJ.csv`).
- `data/sql/create_tables.sql` : tables (`kerofis`, `infos`, `municipalities`, `toponyms`, `toponyms_types`) ; `data/sql/load_tables.sql` : requêtes qui remplissent les tables autres que `kerofis` (exécutées dans l'ordre, ajouter ici les nouvelles) ; `data/sql/create_views.sql` : vues de statistiques.
- Ordre du chargement : tables, CSV dans `kerofis`, `load_tables.sql`, vues. Pour une nouvelle table : la déclarer dans `create_tables.sql` et la remplir dans `load_tables.sql`.
- `data/kerofis.db` : généré, ignoré par git. À recréer sur chaque machine.

## Reprendre sur une nouvelle machine

```bash
git clone https://github.com/osm-bzh/api-kerofis.git
cd api-kerofis
git checkout v2026.10
python -m pip install -r requirements.txt
python scripts/load_csv_into_db.py
python -m uvicorn app.main:app --port 80
```

Puis tester `http://localhost/api-kerofis/infos/`.

Pour voir les requêtes SQL dans la console : `python -m app.main --debug-sql` (options `--port`, `--reload`), ou `KEROFIS_DEBUG_SQL=1` avec uvicorn directement. La sortie vient de `query_db()`.

## Routes existantes

- `GET /api-kerofis/` : accueil.
- `GET /api-kerofis/infos/` : licence, attribution, puis toutes les lignes de la table `infos` (clé/valeur : `kerofis_version`, `import_date`, `municipalities_count`, `toponyms_count`), chacune devenant une clé de la réponse.
- `GET /api-kerofis/municipalities/` : liste de la table `municipalities` (`insee`, `name_br`, `name_fr`, `nb_toponyms`).
- `GET /api-kerofis/municipality/{insee}/` : fiche d'une commune en 3 blocs (`infos`, `statistics`, `toponyms`) ; 404 si aucun toponyme.
- `GET /api-kerofis/municipality/{insee}/infos/`, `.../statistics/`, `.../toponyms/` : chaque bloc séparément (logique partagée dans les fonctions `get_municipality_*`). Les toponymes viennent de la table `toponyms` (`id`, `insee`, `type_br`, `name_br`, `type_fr`, `name_fr`) ; les statistiques de la vue `stats_municipality_type_of_toponyms` (`insee`, `type_br`, `type_fr`, `count`).
- `GET /api-kerofis/search/municipalities/` : recherche de communes (`insee` par préfixe, `name_br` et `name_fr` par « contient », 2 caractères minimum, `sort`) ; réponse `{count, municipalities}`, 200 avec `count` à 0 si rien.
- `GET /api-kerofis/search/toponyms/` : recherche de toponymes (`insee` par préfixe, `name_br`/`name_fr` par « contient », `type` exact sur `type_br`, en minuscules sans accents, via la fonction SQL `normalize()` ; lit la table `toponyms`, `sort`, pagination `limit` 100 par défaut / 1000 max et `offset`) ; réponse `{count, toponyms}` avec `count` = total hors pagination.
- `GET /api-kerofis/docs/` : Swagger (`redoc/` et `openapi.json` sous le même préfixe).

## Points à trancher

- **Doublons de `niv`** : le CSV a plusieurs lignes pour un même identifiant (autres formes bretonnes), alors que `niv` est la clé primaire. Aujourd'hui le script ne garde que la ligne à la date de validation la plus récente (environ 150 lignes perdues). Alternative : changer la clé primaire pour tout conserver.
- **Préfixe `/api-kerofis`** : codé en dur dans l'application. À revoir (`root_path`) si l'API est mise derrière un reverse proxy qui retire déjà ce préfixe.
- **`nb_toponyms` et `toponyms`** : `municipalities` est calculée sur `kerofis` (62 169 lignes) alors que `toponyms` ne garde que les lignes dont le type est connu (JOIN sur `toponyms_types`, 38 lignes sans type exclues) : le nombre annoncé peut dépasser de 1 ou 2 le nombre renvoyé. Calculer `nb_toponyms` depuis `toponyms` les alignerait.
- **Table `infos`** : la clé `kerofis_version` remplace l'ancienne `version_kerofis`. `value` est de type `TEXT` : les compteurs sont renvoyés comme des chaînes (`"2039"`).
- **Pseudo-communes** : `load_tables.sql` supprime de `kerofis` les codes INSEE `98888` et `99999` (étranger, régions…) avant de remplir les autres tables : ces lieux ne sont plus dans l'API. `municipalities` n'a donc plus de doublons de code INSEE (1 361 communes) ; une clé primaire sur `insee` serait possible. À revoir si ces lieux doivent être exposés.
- **Table `kerofis` vidée** : `load_tables.sql` finit par `DELETE FROM kerofis`, donc la table est vide après chargement et le fichier de base garde de l'espace libre (un `VACUUM` le réduirait). Tout ce qui lit `kerofis` après le chargement ne trouve rien.
- **Dependabot** : GitHub signale des alertes de sécurité à l'onglet Security du dépôt (non consultées).

## Conventions

- Code, commentaires et noms en anglais ; messages de commit et documentation en français.
- Licence du code : CeCILL v2.1 (fichier `LICENCE`). Données : ODbL v1.0.
- Données source : lecture en `utf-8-sig` (certains CSV commencent par un BOM), séparateur `;`.
- On ne commite et ne pousse que sur demande.

## Environnement de la machine d'origine

Windows 11, Python 3.14, pandas 3, FastAPI 0.143. Sous Windows, utiliser `python -m pip` (pas de `pip` dans le PATH) et `python -X utf8` pour afficher les accents dans la console.
