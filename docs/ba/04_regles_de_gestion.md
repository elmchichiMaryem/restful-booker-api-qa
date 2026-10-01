# Règles de gestion — API Restful Booker

Une règle de gestion (RG) exprime une contrainte métier que l'API doit respecter, quelle que soit
la façon dont elle est implémentée. Chaque règle indique sa **source** :

| Source | Signification |
|---|---|
| **Documentée** | Énoncée explicitement par la documentation officielle |
| **Hypothèse métier** | Non documentée, mais indispensable pour une réservation d'hôtel (voir hypothèse H4 de la note de cadrage) |
| **Bonne pratique REST** | Non documentée ; on retient le comportement HTTP usuel (voir hypothèse H3) |

La colonne « Constat d'analyse » renvoie aux observations du tableau §5 de
[02_analyse_api.md](02_analyse_api.md). La vérification formelle est faite en Phase 2 ([cas de test](../qa/02_cas_de_test.md)).

---

## 1. Synthèse

| ID | Domaine | Règle (résumé) | Source | US | Constat d'analyse |
|---|---|---|---|---|---|
| RG-01 | Données | Tous les champs d'une réservation sont obligatoires en création et en remplacement | Documentée | US-03, US-08 | ⚠️ obs. 13, 14, 15 |
| RG-02 | Données | `firstname` et `lastname` sont des chaînes de caractères non vides | Documentée (type) + Hypothèse métier (non vide) | US-03, US-08 | ⚠️ obs. 16 |
| RG-03 | Données | `totalprice` est un nombre | Documentée | US-03, US-08 | ⚠️ obs. 17 |
| RG-04 | Données | `totalprice` est positif ou nul | Hypothèse métier | US-03, US-08 | ⚠️ obs. 20 |
| RG-05 | Données | `depositpaid` est un booléen | Documentée | US-03, US-08 | ⚠️ BUG-04 (Phase 2) |
| RG-06 | Dates | `checkin` et `checkout` sont des dates valides au format `AAAA-MM-JJ` | Documentée | US-03, US-08 | ⚠️ obs. 19 |
| RG-07 | Dates | La date de départ est strictement postérieure à la date d'arrivée | Hypothèse métier | US-03, US-08 | ⚠️ obs. 18 |
| RG-08 | Modification | Une modification partielle ne change que les champs fournis | Documentée | US-09 | ✅ obs. 26 |
| RG-09 | Droits | Modifier ou supprimer une réservation exige une authentification valide | Documentée | US-08, US-09, US-10, US-11 | ✅ obs. 23, 24, 27, 28 |
| RG-10 | Droits | Deux moyens d'authentification équivalents : jeton en cookie ou Basic Auth | Documentée | US-02, US-11 | ✅ obs. 22, 26 |
| RG-11 | Droits | Aucun jeton n'est délivré sans identifiants valides | Documentée + Bonne pratique REST (code 401) | US-02 | ⚠️ obs. 3, 4 (code) |
| RG-12 | Cycle de vie | Une réservation supprimée n'est plus consultable | Documentée | US-10 | ✅ obs. 30 |
| RG-13 | Cycle de vie | Une opération sur une réservation inexistante renvoie 404 | Bonne pratique REST | US-04, US-08, US-10 | ⚠️ obs. 25, 31 |
| RG-14 | Cycle de vie | Chaque réservation créée reçoit un identifiant unique attribué par le système | Documentée | US-03 | ✅ |
| RG-15 | Exploitation | L'API expose un contrôle de santé répondant 201 | Documentée | US-01 | ✅ obs. 1 |
| RG-16 | Recherche | Les filtres `firstname` et `lastname` renvoient les réservations correspondantes ; combinés, ils se cumulent (ET logique) | Documentée | US-06 | ✅ obs. 6, 7 |
| RG-17 | Recherche | Les filtres `checkin` et `checkout` renvoient les réservations dont la date est supérieure ou égale à la date fournie | Documentée | US-07 | ⚠️ BUG-11, BUG-12, BUG-13 (Phase 2) |
| RG-18 | Erreurs | Une requête invalide reçoit une erreur client (4xx), jamais une erreur serveur (5xx) | Bonne pratique REST | US-12 | ⚠️ obs. 8, 13, 14, 16 |

Légende : ✅ conforme lors de l'analyse · ⚠️ écart constaté. Les anomalies qualifiées
(BUG-xx) sont détaillées dans [03_rapports_anomalies.md](../qa/03_rapports_anomalies.md).

---

## 2. Détail des règles

### RG-01 — Champs obligatoires

Pour `POST /booking` et `PUT /booking/{id}`, la requête doit contenir les champs suivants :
`firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates.checkin`,
`bookingdates.checkout`, `additionalneeds`.

- **Si un champ est absent** : la requête est rejetée par un code 400 et aucune réservation n'est
  créée ni modifiée.
- **Remarque** : `additionalneeds` est marqué obligatoire dans la documentation, alors qu'une
  demande particulière est facultative par nature. Ce point est à arbitrer avec le métier ; il
  est tracé comme un écart entre documentation et comportement.

### RG-02 — Identité du client

`firstname` et `lastname` sont des chaînes de caractères. Une chaîne vide ne permet pas
d'identifier le client et doit être refusée.

- **Si la règle n'est pas respectée** : code 400.

### RG-03 — Type du prix

`totalprice` est une valeur numérique (entier ou décimal).

- **Si la règle n'est pas respectée** : code 400. La valeur ne doit jamais être remplacée
  silencieusement par `null`.

### RG-04 — Prix positif ou nul

`totalprice` ≥ 0. Un prix négatif n'a pas de sens pour un séjour.

- **Si la règle n'est pas respectée** : code 400.

### RG-05 — Acompte

`depositpaid` est un booléen (`true` ou `false`).

- **Si la règle n'est pas respectée** : code 400.

### RG-06 — Format des dates

`bookingdates.checkin` et `bookingdates.checkout` sont des dates calendaires valides au format
`AAAA-MM-JJ` (ISO 8601). Par exemple, `2026-02-30` n'est pas une date valide.

- **Si la règle n'est pas respectée** : code 400. Une date ne doit jamais être stockée sous une
  forme corrompue.

### RG-07 — Cohérence des dates de séjour

`checkout` > `checkin` : un séjour dure au moins une nuit. La date d'arrivée dans le passé n'est
pas contrôlée, car l'API sert aussi d'historique.

- **Si la règle n'est pas respectée** : code 400 et aucune réservation n'est créée ni modifiée.

### RG-08 — Modification partielle

`PATCH /booking/{id}` ne modifie que les champs présents dans le corps. Les autres champs
conservent leur valeur. La réponse renvoie la réservation complète. Les champs fournis respectent
les règles RG-02 à RG-07.

### RG-09 — Droits nécessaires pour modifier ou supprimer

`PUT`, `PATCH` et `DELETE` sur `/booking/{id}` exigent une authentification valide. Sans
authentification, ou avec une authentification invalide :

- la requête est refusée (code 403 observé ; 401 serait plus précis quand l'authentification est
  absente) ;
- la réservation n'est ni modifiée ni supprimée.

La lecture et la création sont publiques.

### RG-10 — Moyens d'authentification

Deux moyens sont acceptés, de façon équivalente :

1. `Cookie: token=<jeton>`, avec un jeton obtenu par `POST /auth` ;
2. `Authorization: Basic <base64(identifiant:mot_de_passe)>`.

### RG-11 — Délivrance du jeton

`POST /auth` ne délivre un jeton qu'avec un identifiant et un mot de passe valides.

- **Identifiants incorrects** : aucun jeton n'est renvoyé, code 401 attendu.
- **Champs manquants** : aucun jeton n'est renvoyé, code 400 attendu.

### RG-12 — Suppression définitive

Après un `DELETE` réussi (code 201, comme le documente l'API), la réservation n'est plus
consultable (`GET` renvoie 404) et n'apparaît plus dans la liste.

### RG-13 — Ressource inexistante

Toute opération (`GET`, `PUT`, `PATCH`, `DELETE`) sur un identifiant qui ne correspond à aucune
réservation renvoie 404.

### RG-14 — Identifiant de réservation

À la création, le système attribue un `bookingid` entier et unique, renvoyé dans la réponse. Le
consommateur ne fournit jamais l'identifiant.

### RG-15 — Contrôle de santé

`GET /ping` renvoie 201 lorsque l'API est disponible.

### RG-16 — Recherche par nom

- `firstname` et/ou `lastname` en paramètres de `GET /booking` renvoient les identifiants des
  réservations correspondantes.
- Plusieurs filtres se combinent par un ET logique.
- Aucun résultat : code 200 et tableau vide.

### RG-17 — Recherche par dates

- `checkin=D` : réservations dont la date d'arrivée est ≥ D.
- `checkout=D` : réservations dont la date de départ est ≥ D.
- Les dates sont au format `AAAA-MM-JJ` ; une date invalide donne un code 400.

### RG-18 — Gestion des erreurs

Une requête invalide (JSON mal formé, champ manquant, type incorrect, paramètre invalide)
reçoit un code 4xx. Un code 5xx signale un défaut du serveur et ne doit jamais être la réponse à
une erreur du consommateur.
