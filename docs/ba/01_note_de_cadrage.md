# Note de cadrage — Projet de test de l'API Restful Booker

| Élément | Valeur |
|---|---|
| Projet | Recette de l'API de réservation hôtelière Restful Booker |
| Version du document | 1.0 |
| Date | 01/10/2026 |
| Auteure | Maryem Elmchichi (Business Analyst / QA Engineer) |
| API cible | https://restful-booker.herokuapp.com |
| Documentation de référence | https://restful-booker.herokuapp.com/apidoc/index.html |

---

## 1. Contexte

Restful Booker est une API REST de gestion de réservations hôtelières. Elle permet de créer,
consulter, modifier et supprimer des réservations, et de rechercher des réservations par nom
de client ou par dates de séjour. Les opérations de modification et de suppression sont
protégées par une authentification (jeton ou Basic Auth).

Dans ce projet, l'API est traitée comme le **back-end d'un système de réservation** consommé
par plusieurs applications. Elle est publiée publiquement comme terrain d'entraînement au test
d'API : elle est **partagée par de nombreux utilisateurs** et ses données sont **réinitialisées
régulièrement**. Elle contient volontairement des défauts, ce qui en fait un bon support pour
démontrer une démarche de recette complète.

## 2. Objectifs

### 2.1 Objectifs métier

- Garantir que les consommateurs de l'API peuvent gérer le cycle de vie complet d'une
  réservation (création → consultation → modification → suppression).
- Garantir que seules les personnes autorisées peuvent modifier ou supprimer une réservation.
- Garantir que les données de réservation restent cohérentes (champs obligatoires, dates de
  séjour valides).

### 2.2 Objectifs du projet de test

| # | Objectif | Livrable |
|---|---|---|
| O1 | Formaliser le besoin et le comportement attendu de l'API | Analyse, user stories, règles de gestion, OpenAPI |
| O2 | Vérifier la conformité de l'API à sa documentation et aux règles métier | Cas de test exécutés, rapports d'anomalies |
| O3 | Automatiser la non-régression | Collection Postman/Newman, suite pytest |
| O4 | Vérifier le contrat des réponses | Schémas JSON validés automatiquement |
| O5 | Donner une indication des temps de réponse | Test de charge légère k6 et rapport |
| O6 | Exécuter les tests en continu | Pipeline GitHub Actions |

## 3. Périmètre

### 3.1 Dans le périmètre

| Domaine | Endpoints |
|---|---|
| Disponibilité | `GET /ping` |
| Authentification | `POST /auth` |
| Lecture | `GET /booking`, `GET /booking/{id}` |
| Recherche (filtres) | `GET /booking?firstname=&lastname=&checkin=&checkout=` |
| Écriture | `POST /booking`, `PUT /booking/{id}`, `PATCH /booking/{id}`, `DELETE /booking/{id}` |

Types de tests : fonctionnels (positifs et négatifs), sécurité de base (contrôle d'accès),
contrat (structure et types des réponses), performance en charge légère.

Format d'échange principal : **JSON**.

### 3.2 Hors périmètre

- Les formats XML et `application/x-www-form-urlencoded`. Ils sont documentés, mais le JSON
  est le format retenu pour les consommateurs.
- Les tests de charge élevée, de stress ou d'endurance : l'API est publique et partagée.
- Les tests de sécurité avancés (injection, fuzzing, tests d'intrusion).
- L'interface graphique et la base de données sous-jacente (test en boîte noire).

## 4. Parties prenantes

| Partie prenante | Rôle vis-à-vis de l'API | Attentes principales |
|---|---|---|
| **Application front** (site ou application mobile de réservation) | Crée et consulte les réservations des clients | Création fiable, réponses rapides, messages d'erreur exploitables |
| **Partenaires** (agences de voyage, comparateurs) | Recherchent et consultent les réservations par intégration | Filtres fiables, contrat de réponse stable |
| **Administrateur** (back-office hôtelier) | Modifie et supprime les réservations | Accès protégé, modifications fiables, suppression définitive |
| **Équipe QA** | Conçoit, exécute et automatise les tests | Documentation exacte, environnement disponible |
| **Équipe de développement** (fictive) | Corrige les anomalies | Rapports d'anomalies reproductibles |

## 5. Hypothèses

| # | Hypothèse |
|---|---|
| H1 | La documentation officielle (apidoc) constitue la spécification de référence. |
| H2 | Les identifiants de démonstration `admin` / `password123` sont ceux de l'administrateur. |
| H3 | Quand la documentation ne précise pas un comportement (par exemple une erreur de validation), on attend les **pratiques REST usuelles** : 400 pour une requête invalide, 401/403 pour un accès refusé, 404 pour une ressource inexistante. |
| H4 | Les règles métier non documentées mais évidentes pour une réservation d'hôtel (date de départ postérieure à la date d'arrivée, prix positif) sont des exigences du métier. Elles sont signalées comme « hypothèse métier » dans les règles de gestion. |
| H5 | Les données présentes dans l'API ne sont pas maîtrisées : chaque test crée ses propres données et les supprime ensuite. |

## 6. Risques

| # | Risque | Probabilité | Impact | Mesure de réduction |
|---|---|---|---|---|
| R1 | Indisponibilité ou lenteur de l'API (hébergement gratuit, mise en veille) | Moyenne | Élevé | Vérification `GET /ping` avant les campagnes, délais d'attente adaptés, relance |
| R2 | Données modifiées ou supprimées par d'autres utilisateurs pendant un test | Élevée | Moyen | Données propres à chaque test, identifiants uniques, aucune dépendance aux données existantes |
| R3 | Réinitialisation périodique de la base | Élevée | Faible | Tests indépendants, création des données en début de test |
| R4 | Documentation incomplète ou inexacte | Avérée | Moyen | Distinction claire entre comportement documenté, observé et attendu ; écarts tracés en anomalies |
| R5 | Surcharge d'une API partagée par nos tests | Faible | Élevé | Charge limitée à 5 utilisateurs virtuels pendant 30 s, pauses entre requêtes, k6 lancé manuellement uniquement |
| R6 | Résultats de performance non représentatifs | Élevée | Faible | Résultats présentés comme indicatifs |
| R7 | Faille de contrôle d'accès (modification sans droits) | Faible | Critique | Cas de test de sécurité dédiés sur chaque endpoint protégé |

## 7. Livrables et organisation

| Phase | Contenu | Livrables |
|---|---|---|
| 0 | Initialisation | Structure du dépôt, outillage |
| 1 | Analyse métier | Note de cadrage, analyse d'API, OpenAPI, user stories, règles de gestion |
| 2 | Test manuel et exploratoire | Stratégie, cas de test, rapports d'anomalies |
| 3 | Automatisation Postman | Collection, environnement, exécution Newman |
| 4 | Automatisation Python | Client API, tests pytest, schémas JSON, matrice de traçabilité |
| 5 | Performance | Script k6, rapport de performance |
| 6 | Intégration continue et bilan | Pipeline GitHub Actions, bilan de test, README |
