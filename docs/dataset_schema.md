# Dataset – Schéma cible (OpenAgenda → dataset propre)

## Objectif

Définir un schéma de données stable pour stocker les événements récupérés via OpenAgenda.
Ce dataset servira de base à l’indexation vectorielle et au système RAG.

**Périmètre** : Département de l’Hérault (34), période [-365 jours ; +365 jours], tous types d’événements.

---

## Formats de sortie

- **Format principal : JSONL**
  - 1 ligne = 1 événement
  - Encodage UTF-8
- **Format optionnel : CSV**
  - utilisé pour inspection rapide (Excel / pandas)

---

## Champs du dataset

| Champ | Type | Description |
|------|------|-------------|
| event_id | string | Identifiant unique OpenAgenda |
| title | string | Titre nettoyé |
| summary | string | Résumé (description_fr) |
| description | string | Description longue |
| start_datetime | string | Date début |
| end_datetime | string | Date fin (optionnel) |
| location_name | string | Nom du lieu |
| city | string | Ville |
| postal_code | string | Code postal (optionnel) |
| department_code | string | Toujours "34" |
| lat | float | Latitude (optionnel) |
| lon | float | Longitude (optionnel) |
| url | string | URL publique |
| tags | array | Liste de catégories |
| source | string | "openagenda" |
| organizer | string | Organisateur (optionnel) |
| image_url | string | Image (optionnel) |
| price | string | Tarif (optionnel) |
| accessibility | string | Accessibilité (optionnel) |
| updated_at | string | Mise à jour (optionnel) |
| language | string | "fr" |
| retrieval_text | string | Texte pour RAG |


---

## Champ dérivé pour le RAG

### retrieval_text (obligatoire)

**Type : string**

Texte concaténé qui servira à l’indexation vectorielle.
Construit à partir de :
- title (doublé)
- city
- location_name
- tags
- summary
- description
- start_datetime

Objectif : améliorer la recherche vectorielle.

**Objectif** : *maximiser la pertinence sémantique lors des recherches.*

---

## Règles de nettoyage / normalisation

- `title`, `description` : suppression des balises HTML, normalisation des espaces
- dates : conversion en ISO 8601 (timezone Europe/Paris)
- champs manquants :
  - `description` vide → remplacer par chaîne vide (pas null)
  - `end_datetime` absent → autorisé
  - `lat/lon` absents → autorisés
- `tags` : toujours une liste (vide si rien)
- unicité : `event_id` doit être unique dans le dataset final

---

## Contrôles qualité attendus 

- au moins N événements récupérés (N défini après première collecte)
- aucun `event_id` dupliqué
- tous les événements respectent la période [-365 ; +365]
- `title`, `start_datetime`, `url` non vides
- `retrieval_text` non vide

---