# Endpoint

https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records

**Type** : API publique (OpenDataSoft Explore API)
Authentification : *aucune*

---

# Paramètres utilisés

## Filtrage géographique
Le filtrage géographique est appliqué via la clause *where* :

Filtrer les événements situés dans :

```sql
location_countrycode = "FR"
AND location_department = "Hérault"
```

## Filtrage temporel

Filtrage basé sur :

`firstdate_begin`

Période :

- `aujourd’hui - 365 jours`
- `aujourd’hui + 365 jours`

Condition utilisée :

```sql
firstdate_begin >= date'YYYY-MM-DD'
AND firstdate_begin <= date'YYYY-MM-DD'
```

## Pagination

Paramètres utilisés :

`limit = 100`
`offset = 0`

Pagination :
`offset = offset + limit`

## Tri
Tri recommandé :
`order_by = firstdate_begin ASC`

## Gestion des erreurs
- **429** → *attente puis retry*
- **400** → *arrêt propre (souvent lié à pagination ou filtre invalide)*

## Sauvegarde des données RAW

Les événements récupérés seront stockés dans :

data/raw/openagenda_events_YYYY-MM-DD.jsonl

Format :
1 ligne JSON = 1 événement tel que renvoyé par l’API.

Aucune transformation n’est appliquée à ce stade.

---