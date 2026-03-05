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

## Champs obligatoires

| Champ | Type | Description | Exemple |
|------|------|-------------|---------|
| event_id | string | ID stable OpenAgenda | "12345678" |
| title | string | Titre de l’événement | "Concert Jazz" |
| description | string | Description textuelle (nettoyée) | "Soirée jazz..." |
| start_datetime | string (ISO 8601) | Début | "2026-03-10T20:30:00+01:00" |
| end_datetime | string (ISO 8601) | Fin (si dispo) | "2026-03-10T22:30:00+01:00" |
| location_name | string | Nom du lieu | "Zénith Sud" |
| city | string | Ville | "Montpellier" |
| postal_code | string | Code postal (si dispo) | "34000" |
| department_code | string | Code département | "34" |
| lat | float | Latitude (si dispo) | 43.6119 |
| lon | float | Longitude (si dispo) | 3.8772 |
| url | string | URL publique de l’événement | "https://..." |
| tags | array[string] | Mots-clés / catégories | ["musique", "jazz"] |
| source | string | Source des données | "openagenda" |

---

## Champs optionnels (si disponibles)

| Champ | Type | Description |
|------|------|-------------|
| summary | string | résumé court |
| organizer | string | organisateur |
| image_url | string | image principale |
| price | string | information tarifaire |
| accessibility | string | accessibilité |
| updated_at | string (ISO 8601) | dernière mise à jour |
| language | string | langue dominante du contenu |

---

## Champ dérivé pour le RAG

### retrieval_text (obligatoire)

**Type : string**

Texte concaténé qui servira à l’indexation vectorielle.
Construit à partir de champs fiables :

- title
- description
- location_name
- city + postal_code + department_code
- start_datetime / end_datetime
- tags

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