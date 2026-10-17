# API KerOfis

## Description

Cette API met à disposition la base de données de toponymie bretonne « KerOfis », libérée par l'Office public de la langue bretonne (OPLB / Ofis publik ar brezhoneg).

Elle associe les noms de lieux (communes, hameaux, voies, cours d'eau, monuments…) en français à leur forme en breton retenue par l'OPLB.

Le projet charge un export CSV de cette base dans une base SQLite, puis l'expose via une API FastAPI.

## Organisation du projet

```
app/                  application FastAPI
  main.py
scripts/              scripts utilitaires
  load_csv_into_db.py chargement du CSV le plus récent dans la base SQLite
data/
  csv/                exports CSV de l'OPLB (toponymie_lechanvadurezh_AAAAMMJJ.csv)
  sql/                scripts SQL : create_tables.sql, create_views.sql
  kerofis.db          base SQLite (générée, non versionnée)
requirements.txt      dépendances Python
```

## Installation

Prérequis : Python 3.

```bash
pip install -r requirements.txt
```

## Alimenter la base de données

```bash
python scripts/load_csv_into_db.py
```

Le script :

1. recrée la base `data/kerofis.db` (tables et vues, à partir de `data/sql/`) ;
2. cherche dans `data/csv/` le fichier dont la date, dans le nom, est la plus récente ;
3. charge ce fichier dans un dataframe pandas et le nettoie : espaces superflus, valeurs vides, dates au format ISO, reconstitution du nom français (`stumm_orin`) ;
4. écrit le résultat dans la table `kerofis`.

La date du fichier est enregistrée dans la colonne `deiziad_restr` : elle sert de numéro de version des données.

Dans le fichier source, un même identifiant (`niv`) peut apparaître sur plusieurs lignes, quand il existe plusieurs formes bretonnes. Comme `niv` est la clé primaire de la table, seule la ligne dont la date de validation est la plus récente est conservée.

## Lancer l'API

```bash
python -m uvicorn app.main:app --port 8000
```

Ajouter `--reload` pour recharger automatiquement en cas de changement du code source.

L'API répond sous `http://localhost/api-kerofis/`.

## Routes

### `GET /api-kerofis/docs/`

Affiche la documentation de l'API (swagger).

### `GET /api-kerofis/`

Route d'accueil.

### `GET /api-kerofis/infos/`

Informations générales : licence, attribution et version des données (date du dernier fichier importé).

```json
{
  "attribution_br": "KerOfis gant osm-bzh",
  "attribution_en": "KerOfis by osm-bzh",
  "attribution_fr": "KerOfis par osm-bzh",
  "version_kerofis": "2026-09-25",
  "licence": "Open Database License (ODbL) v1.0",
  "name": "KerOfis data provided by Ofis publik ar brezhoneg"
}
```

### `GET /api-kerofis/municipalities/`

Liste des communes : code INSEE, nom breton, nom français et nombre de toponymes.

```json
[
  {"insee": "22001", "name_br": "Alineg", "name_fr": "Allineuc", "nb_toponyms": 5},
  {"insee": "22002", "name_br": "Andel", "name_fr": "Andel", "nb_toponyms": 1}
]
```

### `GET /api-kerofis/municipality/{insee}/`

Fiche complète d'une commune (infos, statistiques et toponymes), à partir de son code INSEE. La réponse contient :

- `infos` : informations sur la commune (code INSEE, nom breton, nom français, nombre de toponymes), en premier ;
- `statistics` : nombre de toponymes par type (`rummad`) ;
- `toponyms` : tous les toponymes de la commune, triés par `lec_hanv`.

Renvoie une erreur 404 si le code ne correspond à aucun toponyme.

```json
{
  "infos": {"insee": "22002", "name_br": "Andel", "name_fr": "Andel", "nb_toponyms": 1},
  "statistics": [
    {"insee": "22002", "rummad": "Kumun", "nb": 1}
  ],
  "toponyms": [
    {
      "niv": 3679,
      "deiziad_degemer": "1987-05-02",
      "insee": "22002",
      "kumun": "Andel",
      "stagadenn": null,
      "lec_hanv": "Andel",
      "stumm_orin": "Andel",
      "rummad": "Kumun",
      "stumm_dibab": "Andel"
    }
  ]
}
```

### `GET /api-kerofis/municipality/{insee}/infos/`

Informations sur une commune : bloc `infos` de la route précédente. Renvoie une erreur 404 si le code INSEE est inconnu.

```json
{"insee": "22002", "name_br": "Andel", "name_fr": "Andel", "nb_toponyms": 1}
```

### `GET /api-kerofis/municipality/{insee}/statistics/`

Nombre de toponymes par type (`rummad`) pour une commune : bloc `statistics` de la route précédente. Renvoie une erreur 404 si le code INSEE est inconnu.

```json
[
  {"insee": "22002", "rummad": "Kumun", "nb": 1}
]
```

### `GET /api-kerofis/municipality/{insee}/toponyms/`

Tous les toponymes d'une commune, triés par `lec_hanv` : bloc `toponyms` de la route précédente. Renvoie une erreur 404 si le code INSEE est inconnu.

```json
[
  {
    "niv": 3679,
    "deiziad_degemer": "1987-05-02",
    "insee": "22002",
    "kumun": "Andel",
    "stagadenn": null,
    "lec_hanv": "Andel",
    "stumm_orin": "Andel",
    "rummad": "Kumun",
    "stumm_dibab": "Andel"
  }
]
```

## Licences

- **Code** : [CeCILL v2.1](LICENCE).
- **Données** : Open Database License (ODbL) v1.0, fournies par l'Office public de la langue bretonne.
