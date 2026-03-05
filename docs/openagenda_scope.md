# OpenAgenda – Scope de récupération des données

## Objectif

Définir le périmètre de récupération des événements depuis l'API OpenAgenda pour le Proof of Concept du système RAG Puls-Events.

Les données récupérées serviront à construire un dataset d'événements culturels propre et structuré qui sera utilisé pour l'indexation vectorielle lors des étapes suivantes du projet.

---

## Localisation

Le périmètre géographique choisi pour ce POC est :

**Département de l’Hérault (34), France**

Ce choix permet de récupérer un volume d'événements suffisant pour tester le système de recherche sémantique tout en gardant un périmètre raisonnable.

---

## Période de récupération

Les événements récupérés doivent couvrir :

- **Historique :** de *aujourd’hui – 365 jours*
- **À venir :** de *aujourd’hui + 365 jours*

Ce choix permet d'inclure :

- des événements passés récents (historique)
- des événements futurs (cas d'usage principal pour les recommandations)

---

## Type d'événements

Pour ce POC :

**Tous les types d'événements sont inclus**

Aucun filtrage par catégorie n’est appliqué à ce stade.

---

## Limitation du nombre d'événements

Aucune limite maximale d'événements n’est définie.

La récupération des données se fera via le mécanisme de pagination de l’API OpenAgenda si nécessaire.

---

## Utilisation des données

Les événements récupérés seront ensuite :

1. nettoyés et normalisés
2. structurés dans un dataset exploitable
3. préparés pour la vectorisation des descriptions
4. indexés dans une base vectorielle FAISS pour la recherche sémantique

---

## Étapes suivantes

Après la récupération des événements :

1. Nettoyage et validation des données
2. Structuration du dataset final
3. Découpage des textes en *chunks*
4. Vectorisation des descriptions
5. Indexation dans FAISS