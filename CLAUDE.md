# CLAUDE.md

Contexte pour reprendre le projet avec Claude Code sur un autre ordinateur.

## Le projet

API FastAPI qui expose la toponymie bretonne KerOfis (Office public de la langue bretonne). Les données viennent d'exports CSV, chargés dans une base SQLite. Voir [README.md](README.md) pour la description complète, l'installation et les routes.

Le projet a été remis à zéro sur la branche `v2026.10` (commit « RAZ du projet »). L'ancien code (Flask, Python 2, PostgreSQL) reste sur `master` et **ne doit pas servir de base** : on repart d'une API neuve. On l'a seulement consulté pour reprendre les scripts SQL (`setup/create_database.sql`, `setup/create_views.sql`), déjà adaptés à SQLite.

## Organisation

- `app/main.py` : application FastAPI. Toutes les routes sont sous le préfixe `/api-kerofis` (constante `API_PREFIX`). L'accès à la base passe par `query_db()` (lecture seule).
- `scripts/load_csv_into_db.py` : recrée `data/kerofis.db` à partir du CSV le plus récent de `data/csv/` (date dans le nom `..._AAAAMMJJ.csv`).
- `data/sql/create_tables.sql`, `data/sql/create_views.sql` : schéma SQLite.
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
- `GET /api-kerofis/infos/` : licence, attribution, `version_kerofis` (lue dans la vue `infos_file_import`).
- `GET /api-kerofis/municipalities/` : liste de la table `municipalities` (`insee`, `name_br`, `name_fr`, `nb_toponyms`).
- `GET /api-kerofis/municipality/{insee}/` : fiche d'une commune en 3 blocs (`infos`, `statistics`, `toponyms`) ; 404 si aucun toponyme.
- `GET /api-kerofis/municipality/{insee}/infos/`, `.../statistics/`, `.../toponyms/` : chaque bloc séparément (logique partagée dans les fonctions `get_municipality_*`).
- `GET /api-kerofis/search/municipalities/` : recherche de communes (`insee` par préfixe, `name_br` et `name_fr` par « contient », 2 caractères minimum, `sort`) ; réponse `{count, municipalities}`, 200 avec `count` à 0 si rien.
- `GET /api-kerofis/search/toponyms/` : recherche de toponymes (`insee` par préfixe, `name_br`/`name_fr` par « contient » sur `stumm_dibab`/`stumm_orin`, `type` exact en minuscules sans accents sur `rummad` via la fonction SQL `normalize()`, `sort`, pagination `limit` 100 par défaut / 1000 max et `offset`) ; réponse `{count, toponyms}` avec `count` = total hors pagination.
- `GET /api-kerofis/docs/` : Swagger (`redoc/` et `openapi.json` sous le même préfixe).

## Points à trancher

- **Doublons de `niv`** : le CSV a plusieurs lignes pour un même identifiant (autres formes bretonnes), alors que `niv` est la clé primaire. Aujourd'hui le script ne garde que la ligne à la date de validation la plus récente (environ 150 lignes perdues). Alternative : changer la clé primaire pour tout conserver.
- **Préfixe `/api-kerofis`** : codé en dur dans l'application. À revoir (`root_path`) si l'API est mise derrière un reverse proxy qui retire déjà ce préfixe.
- **Code INSEE `99999`** : désigne des lieux hors commune (étranger, régions…) ; ils apparaissent dans `/municipalities/`. Filtrer ou non, à décider.
- **Dependabot** : GitHub signale des alertes de sécurité à l'onglet Security du dépôt (non consultées).

## Conventions

- Code, commentaires et noms en anglais ; messages de commit et documentation en français.
- Licence du code : CeCILL v2.1 (fichier `LICENCE`). Données : ODbL v1.0.
- Données source : lecture en `utf-8-sig` (certains CSV commencent par un BOM), séparateur `;`.
- On ne commite et ne pousse que sur demande.

## Environnement de la machine d'origine

Windows 11, Python 3.14, pandas 3, FastAPI 0.143. Sous Windows, utiliser `python -m pip` (pas de `pip` dans le PATH) et `python -X utf8` pour afficher les accents dans la console.
