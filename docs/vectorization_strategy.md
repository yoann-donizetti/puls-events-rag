# Vectorization Strategy

## Source dataset

Les événements vectorisés proviennent du dataset normalisé :

data/processed/events_*.jsonl

## Texte vectorisé

Le champ utilisé pour la vectorisation est :

retrieval_text

Ce champ concatène les informations principales :

- title
- description
- location
- city
- postal_code
- start_datetime
- tags

Il permet d’optimiser la recherche sémantique.

## Métadonnées conservées

Les métadonnées associées aux vecteurs sont :

- event_id
- title
- start_datetime
- end_datetime
- location_name
- city
- postal_code
- department_code
- url
- source

Ces informations sont utilisées pour reconstruire la réponse dans le système RAG.

## Chunking

Avant la vectorisation, les textes sont découpés en segments appelés chunks afin d’améliorer la qualité de la recherche sémantique.
Les modèles d’embeddings fonctionnent mieux avec des textes de taille raisonnable. Un texte trop long peut diluer l’information et réduire la précision de la recherche.
Les paramètres utilisés sont :

chunk_size = 500
chunk_overlap = 50

### chunk_size
*chunk_size* correspond à la taille maximale d’un segment de texte (500 caractères).
Ce choix permet de conserver suffisamment de contexte tout en évitant des segments trop longs.


### chunk_overlap
*chunk_overlap* correspond à la partie de texte répétée entre deux chunks (50 caractères).
Ce chevauchement permet de préserver le contexte lorsque le texte est découpé.

### Justification
Ces paramètres constituent un compromis adapté au dataset d’événements :
la plupart des événements tiennent dans 1 ou 2 chunks
le chevauchement conserve la cohérence du texte
le nombre total de chunks reste raisonnable pour l’index FAISS