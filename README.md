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
  sql/                scripts SQL : create_tables.sql, load_tables.sql, create_views.sql
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

1. recrée la base `data/kerofis.db` : supprime l'ancien fichier, puis crée les tables avec `data/sql/create_tables.sql` ;
2. cherche dans `data/csv/` le fichier dont la date, dans le nom, est la plus récente ;
3. charge ce fichier dans un dataframe pandas et le nettoie : espaces superflus, valeurs vides, dates au format ISO, reconstitution du nom français (`stumm_orin`) ;
4. écrit le résultat dans la table `kerofis` ;
5. exécute les requêtes de `data/sql/load_tables.sql`, qui alimentent les autres tables à partir de la table `kerofis` ;
6. crée les vues avec `data/sql/create_views.sql`.

### Les tables

- `kerofis` : les données du CSV, une ligne par toponyme.
- `toponyms` : table dérivée de `kerofis` (identifiant, code INSEE, type et nom en breton, type et nom en français), remplie par `data/sql/load_tables.sql`.
`load_tables.sql` peut contenir plusieurs requêtes : elles sont toutes exécutées, dans l'ordre du fichier, après le chargement de `kerofis` et avant la création des vues. Une vue peut donc s'appuyer sur ces tables.

La date du fichier est enregistrée dans la colonne `deiziad_restr` : elle sert de numéro de version des données.

Dans le fichier source, un même identifiant (`niv`) peut apparaître sur plusieurs lignes, quand il existe plusieurs formes bretonnes. Comme `niv` est la clé primaire de la table, seule la ligne dont la date de validation est la plus récente est conservée.

## Lancer l'API

```bash
python -m uvicorn app.main:app --port 8000
```

Ajouter `--reload` pour recharger automatiquement en cas de changement du code source.

### Afficher les requêtes SQL (mode debug)

Pour afficher dans la console chaque requête SQL envoyée à la base, lancer l'API avec le lanceur intégré :

```bash
python -m app.main --debug-sql
```

Ce lanceur accepte aussi `--port` (80 par défaut) et `--reload`. Exemple : `python -m app.main --debug-sql --port 8000 --reload`.

Chaque requête est affichée sur une ligne `[SQL]`, avec ses paramètres déjà remplacés :

```
[SQL] SELECT insee, name_br, name_fr, nb_toponyms FROM municipality WHERE insee = '29024'
```

`uvicorn` refuse les options qu'il ne connaît pas : avec la commande `uvicorn` directe, activer le mode avec la variable d'environnement `KEROFIS_DEBUG_SQL=1`.

```bash
KEROFIS_DEBUG_SQL=1 python -m uvicorn app.main:app --port 8000
```

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
  {"insee": "29023", "name_br": "Karanteg", "name_fr": "Carantec", "nb_toponyms": 30},
  {"insee": "29024", "name_br": "Karaez-Plougêr", "name_fr": "Carhaix-Plouguer", "nb_toponyms": 498}
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
  "infos": {
    "insee": "29024",
    "name_br": "Karaez-Plougêr",
    "name_fr": "Carhaix-Plouguer",
    "nb_toponyms": 498
  },
  "statistics": [
    {
      "insee": "29024",
      "rummad": "Diseurt",
      "nb": 4
    },
    {
      "insee": "29024",
      "rummad": "Hent",
      "nb": 314
    },
    {
      "insee": "29024",
      "rummad": "Karter",
      "nb": 6
    },
    {
      "insee": "29024",
      "rummad": "Koad",
      "nb": 1
    },
    {
      "insee": "29024",
      "rummad": "Kumun",
      "nb": 1
    },
    {
      "insee": "29024",
      "rummad": "Kêriadenn",
      "nb": 80
    },
    {
      "insee": "29024",
      "rummad": "Maez",
      "nb": 11
    },
    {
      "insee": "29024",
      "rummad": "Monumant/Savadur",
      "nb": 63
    },
    {
      "insee": "29024",
      "rummad": "Takad",
      "nb": 18
    }
  ],
  "toponyms": [
    {
      "niv": 46627,
      "deiziad_degemer": "2007-01-01",
      "insee": "29024",
      "kumun": "Karaez-Plougêr",
      "stagadenn": "Place du",
      "lec_hanv": "19-mars-62",
      "stumm_orin": "Place du 19-mars-62",
      "rummad": "Hent",
      "stumm_dibab": "Plasenn an 19 a viz Meurzh 1962"
    },
    {
      "niv": 46440,
      "deiziad_degemer": "2007-01-01",
      "insee": "29024",
      "kumun": "Karaez-Plougêr",
      "stagadenn": "Rue de l'",
      "lec_hanv": "Abattoir",
      "stumm_orin": "Rue de l'Abattoir",
      "rummad": "Hent",
      "stumm_dibab": "Straed an Ti-lazhañ"
    }
  ]
}
```

La liste est abrégée dans cet exemple : la commune compte 498 toponymes.

### `GET /api-kerofis/municipality/{insee}/infos/`

Informations sur une commune : bloc `infos` de la route précédente. Renvoie une erreur 404 si le code INSEE est inconnu.

```json
{"insee": "29024", "name_br": "Karaez-Plougêr", "name_fr": "Carhaix-Plouguer", "nb_toponyms": 498}
```

### `GET /api-kerofis/municipality/{insee}/statistics/`

Nombre de toponymes par type (`rummad`) pour une commune : bloc `statistics` de la route précédente. Renvoie une erreur 404 si le code INSEE est inconnu.

```json
[
  {"insee": "29024", "rummad": "Diseurt", "nb": 4},
  {"insee": "29024", "rummad": "Hent", "nb": 314},
  {"insee": "29024", "rummad": "Karter", "nb": 6},
  {"insee": "29024", "rummad": "Koad", "nb": 1},
  {"insee": "29024", "rummad": "Kumun", "nb": 1},
  {"insee": "29024", "rummad": "Kêriadenn", "nb": 80},
  {"insee": "29024", "rummad": "Maez", "nb": 11},
  {"insee": "29024", "rummad": "Monumant/Savadur", "nb": 63},
  {"insee": "29024", "rummad": "Takad", "nb": 18}
]
```

### `GET /api-kerofis/municipality/{insee}/toponyms/`

Tous les toponymes d'une commune, triés par `lec_hanv` : bloc `toponyms` de la route précédente. Renvoie une erreur 404 si le code INSEE est inconnu.

```json
[
  {
    "niv": 46627,
    "deiziad_degemer": "2007-01-01",
    "insee": "29024",
    "kumun": "Karaez-Plougêr",
    "stagadenn": "Place du",
    "lec_hanv": "19-mars-62",
    "stumm_orin": "Place du 19-mars-62",
    "rummad": "Hent",
    "stumm_dibab": "Plasenn an 19 a viz Meurzh 1962"
  },
  {
    "niv": 46440,
    "deiziad_degemer": "2007-01-01",
    "insee": "29024",
    "kumun": "Karaez-Plougêr",
    "stagadenn": "Rue de l'",
    "lec_hanv": "Abattoir",
    "stumm_orin": "Rue de l'Abattoir",
    "rummad": "Hent",
    "stumm_dibab": "Straed an Ti-lazhañ"
  }
]
```

La liste est abrégée dans cet exemple : la commune compte 498 toponymes.

### `GET /api-kerofis/search/municipalities/`

Recherche de communes. Au moins un critère est obligatoire. Plusieurs critères se combinent (ET).

| Paramètre | Recherche | Exemple |
|---|---|---|
| `insee` | le code INSEE commence par la valeur (`29` : tout le département) | `insee=29` |
| `name_br` | le nom breton contient la valeur | `name_br=plouha` |
| `name_fr` | le nom français contient la valeur | `name_fr=carhaix` |
| `sort` | critère de tri : `insee`, `name_br` ou `name_fr` (défaut : `name_br`) | `sort=name_fr` |

Chaque critère de recherche doit avoir au moins 2 caractères (sinon erreur 422). Un critère manquant donne aussi une erreur 422. Si rien n'est trouvé, la réponse est `200` avec `count` à 0 et une liste vide.

Exemples :

- les communes dont le nom breton contient `plouha` : `/api-kerofis/search/municipalities/?name_br=plouha`
- les communes du Finistère dont le nom français contient `plou`, triées par nom français : `/api-kerofis/search/municipalities/?insee=29&name_fr=plou&sort=name_fr`

La réponse contient `count` (nombre de communes trouvées) en premier, puis `municipalities` (la liste des communes) :

```json
{
  "count": 2,
  "municipalities": [
    {"insee": "22222", "name_br": "Plouha", "name_fr": "Plouha", "nb_toponyms": 42},
    {"insee": "56168", "name_br": "Plouharnel", "name_fr": "Plouharnel", "nb_toponyms": 31}
  ]
}
```

La casse n'est ignorée que pour les caractères ASCII : `plouger` ne trouve pas `Plougêr`.

### `GET /api-kerofis/search/toponyms/`

Recherche de toponymes. Au moins un critère est obligatoire. Plusieurs critères se combinent (ET).

| Paramètre | Recherche | Exemple |
|---|---|---|
| `insee` | le code INSEE commence par la valeur (`29` : tout le département) | `insee=29024` |
| `name_br` | le nom breton (`stumm_dibab`) contient la valeur | `name_br=iliz` |
| `name_fr` | le nom français (`stumm_orin`) contient la valeur | `name_fr=abattoir` |
| `type` | le type (`rummad`) est égal à la valeur, en minuscules et sans accents | `type=keriadenn` |
| `sort` | critère de tri : `insee`, `name_br` ou `name_fr` (défaut : `name_br`) | `sort=name_fr` |
| `limit` | nombre maximum de toponymes renvoyés : de 1 à 1000 (défaut : 100) | `limit=20` |
| `offset` | rang du premier toponyme renvoyé, pour la pagination (défaut : 0) | `offset=20` |

Chaque critère texte (`insee`, `name_br`, `name_fr`, `type`) doit avoir au moins 2 caractères (sinon erreur 422). Un critère manquant donne aussi une erreur 422. Si rien n'est trouvé, la réponse est `200` avec `count` à 0 et une liste vide.

Le type est comparé sans tenir compte des accents ni de la casse : `keriadenn` et `Kêriadenn` donnent le même résultat. Exemples de types : `hent` (voies), `keriadenn` (lieux-dits), `monumant/savadur`, `dour`, `karter`.

Exemples :

- les lieux-dits de Carhaix-Plouguer : `/api-kerofis/search/toponyms/?insee=29024&type=keriadenn`
- les toponymes dont le nom français contient `abattoir` : `/api-kerofis/search/toponyms/?name_fr=abattoir`
- la deuxième page de 20 toponymes dont le nom breton contient `iliz` : `/api-kerofis/search/toponyms/?name_br=iliz&limit=20&offset=20`

La réponse contient `count` en premier, puis `toponyms`. `count` est le nombre total de toponymes trouvés, quelle que soit la pagination : la liste `toponyms` peut en contenir moins (`limit`).

```json
{
  "count": 80,
  "toponyms": [
    {
      "niv": 76994,
      "deiziad_degemer": "2013-06-18",
      "insee": "29024",
      "kumun": "Karaez-Plougêr",
      "stagadenn": "Aux",
      "lec_hanv": "Dépendances de Persivien",
      "stumm_orin": "Aux Dépendances de Persivien",
      "rummad": "Kêriadenn",
      "stumm_dibab": "Somachoù Persivien"
    },
    {
      "niv": 30871,
      "deiziad_degemer": "2011-06-27",
      "insee": "29024",
      "kumun": "Karaez-Plougêr",
      "stagadenn": null,
      "lec_hanv": "Caborgnès",
      "stumm_orin": "Caborgnès",
      "rummad": "Kêriadenn",
      "stumm_dibab": "Kaborgnez"
    }
  ]
}
```

Cet exemple correspond à `?insee=29024&type=keriadenn&sort=name_fr&limit=2` (liste abrégée à 2 toponymes). Comme pour les communes, la casse n'est ignorée que pour les caractères ASCII dans `name_br` et `name_fr`.

## Licences

- **Code** : [CeCILL v2.1](LICENCE).
- **Données** : Open Database License (ODbL) v1.0, fournies par l'Office public de la langue bretonne.
