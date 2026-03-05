# Endpoint

https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records

**Type** : API publique (OpenDataSoft Explore API)
Authentification : *aucune*

---

# Paramètres utilisés

## Localisation

Filtrer les événements situés dans :
- refine.location_department=Hérault (département de l’Hérault)

## Période

Filtrage basé sur la date de début de l'événement :

`firstdate_begin`

Période ciblée :

- `aujourd’hui - 365 jours`
- `aujourd’hui + 365 jours`

Le filtre temporel sera appliqué via un *where* sur *firstdate_begin* (date de début)

## Pagination

Paramètres utilisés :

`limit = 100`
`offset = 0`

Pagination :
`offset = offset + limit`

## Tri
Tri recommandé :
`order_by = firstdate_begin ASC`

## Sauvegarde des données RAW

Les événements récupérés seront stockés dans :

data/raw/openagenda_events_YYYY-MM-DD.jsonl

Format :
1 ligne JSON = 1 événement tel que renvoyé par l’API.

Aucune transformation n’est appliquée à ce stade.