# API

## API KerOfis
API sur la base de données "kerOfis" libérée par l'Office publique de la langue bretonne (OPLB). Cette API offre les méthodes suivantes :

``` /kerofis/ ```

[TODO]

``` /kerofis/infos/ ```

Retourne un ensemble d'informations globales sur la base de données :
  - date du dernier import de données
  - liste des dates de tous les imports / mises à jour de la base de données

```json
{
  "attribution_br": "kerOfis gant osm-br", 
  "attribution_en": "kerOfis by osm-br", 
  "attribution_fr": "kerOfis par osm-br", 
  "file_imports": {}, 
  "last_file_import": "2016-02-08", 
  "licence": "Licence Ouverte / Open Licence", 
  "name": "kerofis database"
}
```

``` /kerofis/stats/ ```

[TODO]

``` /kerofis/search/ ```

[TODO]

``` /kerofis/municipalities ```

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

``` /kerofis/municipalities/search/ ```

Renvoie une liste de communes, en fonction de 3 critères de recherche :
- code insee :  ```insee={insee}```
- nom en breton : ```name:br={name:br}```
- nom en français : ```name:fr={name:fr}```

Si le code INSEE ne contient que 2 chiffres, une recherche départementale sera effectuée. Exemple : _/kerofis/municipalities/search/?insee=29_


