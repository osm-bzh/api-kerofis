# API KerOfis

## Description
Cette API utilise la base de données "KerOfis" libérée par l'Office public de la langue bretonne (OPLB).
Le jeu de données est disponible sur [cette page](http://www.brezhoneg.bzh/211-roadennou-frank-a-wiriou.htm).


## Utilisation

Cette API offre les méthodes suivantes :

### /kerofis/

[TODO]

### /kerofis/infos/

Retourne un ensemble d'informations globales sur la base de données :

- date du dernier import de données
- liste des dates de tous les imports / mises à jour de la base de données

```json
{
  "attribution_br": "KerOfis gant osm-bzh", 
  "attribution_en": "KerOfis by osm-bzh", 
  "attribution_fr": "KerOfis par osm-bzh", 
  "file_imports": {}, 
  "last_file_import": "2017-10-31", 
  "licence": "Open Database License (ODbL) v1.0", 
  "name": "KerOfis data provided by Ofis publik ar brezhoneg"
}
```

### /kerofis/stats/ 

[TODO]

### /kerofis/search/ 

[TODO]

### /kerofis/municipalities/ 

Renvoie la liste (non paginée) de toutes les communes contenues dans la base de données.

```json
{
  "attribution_br": "kerOfis gant osm-br", 
  "attribution_en": "kerOfis by osm-br", 
  "attribution_fr": "kerOfis par osm-br", 
  "count": "4", 
  "licence": "Licence Ouverte / Open Licence", 
  "municipalities": [
    "{'insee':'29152','name:br':'Motrev','name:fr':'Motreff','nb': 83}", 
    "{'insee':'29174','name:br':'Ploneour-Lanwern','name:fr':'Plon\u00e9our-Lanvern','nb': 481}", 
    "{'insee':'29212','name:br':'Plouzane','name:fr':'Plouzan\u00e9','nb': 196}", 
    "{'insee':'35047','name:br':'Bruz','name:fr':'Bruz','nb': 55}"
  ]
}
```


### /kerofis/municipalities/search/?

Renvoie une liste de communes, en fonction de 4 critères de recherche :
- code insee :  ```insee={insee}```
- nom en breton : ```name:br={name:br}```
- nom en français : ```name:fr={name:fr}```
- langue de recherche : ```lang=fr``` ou ```lang=br``` 

Si le code INSEE ne contient que 2 chiffres, une recherche départementale sera effectuée. Exemple : _/kerofis/municipalities/search/?insee=29_

Exemples :

- la liste des communes dans le Finistère : ```/kerofis/municipalities/search/?insee=29```
- la liste des communes qui commence par plou : ```/kerofis/municipalities/search/?name:fr=plou```
- recherche des voies dont le nom en fr contient min : ```/kerofis/search/?insee=*&lang=fr&name=min```
- recherche des voies dont le nom en br contient min : ```/kerofis/search/?insee=*&lang=br&name=min```
- toutes les voies d’une commune : ```/kerofis/search/?insee=29152&lang=br&name=*```
- liste des objets contenant "maner" sur Ploneour-Lanwern : ```/kerofis/search/?insee=29174&lang=br&name=maner```
- liste des lieux-dits contenant "maner" sur Ploneour-Lanwern : ```/kerofis/search/?insee=29174&lang=br&name=maner&type=K%C3%AAriadenn```
- liste des rues contenant "maner" sur Ploneour-Lanwern : ```/kerofis/search/?insee=29174&lang=br&name=maner&type=Hent```



## Installation

### Prérequis

* PostgreSQL > 9.4
* Python 2.7
  * psycopg2


### En mode stand-alone avec virtualenv

```
# get the code
git clone https://github.com/osm-bzh/api-kerofis.git
cd api-kerofis

# set up phyton venv
virtualenv venv

# install flask and psycopg2
pip install flask psycopg2

# turn on venv
. venv/bin/activate

# tell your terminal the application to work with by exporting the FLASK_APP environment variable
export FLASK_APP=kerofis.py
 
# launch flask
flask run
 * Serving Flask app "kerofis"
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Ouvrir un navigateur et aller sur http://127.0.0.1:5000/kerofis/


