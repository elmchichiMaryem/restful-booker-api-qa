# Analyse de l'API Restful Booker

| Élément | Valeur |
|---|---|
| URL de base | `https://restful-booker.herokuapp.com` |
| Source documentaire | https://restful-booker.herokuapp.com/apidoc/index.html (apidoc, version 1.0.0) |
| Date des observations | 01/10/2026 |
| Méthode d'observation | Requêtes `curl` réelles, sur des réservations créées pour l'occasion puis supprimées |

> **Convention.** Ce document distingue le comportement **documenté** (ce que dit l'apidoc) du
> comportement **observé** (ce que l'API renvoie réellement). Les écarts relevés ici sont des
> **constats d'analyse**. Ils seront rejoués, qualifiés (sévérité, priorité) et formalisés en
> anomalies (BUG-xx) pendant la Phase 2.

---

## 1. Vue d'ensemble des endpoints

| # | Méthode | Endpoint | Rôle | Authentification |
|---|---|---|---|---|
| E1 | `GET` | `/ping` | Vérifier que l'API est disponible | Non |
| E2 | `POST` | `/auth` | Obtenir un jeton d'authentification | Non (identifiants dans le corps) |
| E3 | `GET` | `/booking` | Lister les identifiants de réservation, avec filtres optionnels | Non |
| E4 | `GET` | `/booking/{id}` | Lire une réservation | Non |
| E5 | `POST` | `/booking` | Créer une réservation | Non |
| E6 | `PUT` | `/booking/{id}` | Remplacer entièrement une réservation | **Oui** |
| E7 | `PATCH` | `/booking/{id}` | Modifier partiellement une réservation | **Oui** |
| E8 | `DELETE` | `/booking/{id}` | Supprimer une réservation | **Oui** |

## 2. Modèle de données : la réservation (`Booking`)

| Champ | Type | Obligatoire en création | Exemple | Description |
|---|---|---|---|---|
| `firstname` | chaîne | Oui | `"Jim"` | Prénom du client |
| `lastname` | chaîne | Oui | `"Brown"` | Nom du client |
| `totalprice` | nombre | Oui | `111` | Prix total du séjour |
| `depositpaid` | booléen | Oui | `true` | Acompte versé ou non |
| `bookingdates` | objet | Oui | — | Dates du séjour |
| `bookingdates.checkin` | date `AAAA-MM-JJ` | Oui | `"2018-01-01"` | Date d'arrivée |
| `bookingdates.checkout` | date `AAAA-MM-JJ` | Oui | `"2019-01-01"` | Date de départ |
| `additionalneeds` | chaîne | Oui selon la doc | `"Breakfast"` | Demandes particulières |

Réponse à la création (`POST /booking`) :

```json
{
  "bookingid": 1,
  "booking": {
    "firstname": "Jim",
    "lastname": "Brown",
    "totalprice": 111,
    "depositpaid": true,
    "bookingdates": { "checkin": "2018-01-01", "checkout": "2019-01-01" },
    "additionalneeds": "Breakfast"
  }
}
```

Les réponses de `GET`, `PUT` et `PATCH /booking/{id}` renvoient l'objet `Booking` seul, sans
`bookingid`.

## 3. Détail des endpoints

### E1 — `GET /ping`

- **Rôle** : vérifier l'état de santé de l'API (*health check*).
- **Paramètres** : aucun.
- **Réponse documentée** : `201 Created`, corps `Created`.

### E2 — `POST /auth`

- **En-tête** : `Content-Type: application/json`.
- **Corps** : `{ "username": "admin", "password": "password123" }`.
- **Réponse documentée** : `200 OK`, corps `{ "token": "abc123" }`.
- **Remarque** : le jeton s'utilise ensuite dans l'en-tête `Cookie: token=<jeton>`.

### E3 — `GET /booking`

| Paramètre de requête | Type | Règle documentée |
|---|---|---|
| `firstname` | chaîne | Réservations ayant ce prénom |
| `lastname` | chaîne | Réservations ayant ce nom |
| `checkin` | date `CCYY-MM-DD` | Réservations dont la date d'arrivée est **supérieure ou égale** à la date fournie |
| `checkout` | date `CCYY-MM-DD` | Réservations dont la date de départ est **supérieure ou égale** à la date fournie |

- **Réponse documentée** : `200 OK`, tableau `[{ "bookingid": 1 }, …]`.
- Les filtres sont cumulables (exemple documenté : `?firstname=sally&lastname=brown`).

### E4 — `GET /booking/{id}`

- **En-tête** : `Accept: application/json` (ou `application/xml`).
- **Réponse documentée** : `200 OK`, objet `Booking`.

### E5 — `POST /booking`

- **En-têtes** : `Content-Type` (`application/json`, `text/xml` ou
  `application/x-www-form-urlencoded`) et `Accept`.
- **Corps** : objet `Booking` complet.
- **Réponse documentée** : `200 OK`, objet `{ bookingid, booking }`.

### E6 — `PUT /booking/{id}`

- **Authentification** : `Cookie: token=<jeton>` **ou** `Authorization: Basic <base64>`.
- **Corps** : objet `Booking` **complet** (tous les champs sont marqués obligatoires).
- **Réponse documentée** : `200 OK`, objet `Booking` mis à jour.

### E7 — `PATCH /booking/{id}`

- **Authentification** : identique à E6.
- **Corps** : uniquement les champs à modifier (tous optionnels).
- **Réponse documentée** : `200 OK`, objet `Booking` complet après modification.

### E8 — `DELETE /booking/{id}`

- **Authentification** : identique à E6.
- **Réponse documentée** : `201 Created` (et non `200` ou `204`, qui seraient l'usage REST
  courant). C'est le comportement documenté, donc il est conforme ; c'est un choix de conception
  discutable.

## 4. Authentification

L'API propose deux mécanismes, **interchangeables**, pour les opérations protégées (E6, E7, E8) :

| Mécanisme | En-tête | Obtention |
|---|---|---|
| Jeton de session | `Cookie: token=<jeton>` | `POST /auth` avec les identifiants |
| Basic Auth | `Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=` | Encodage Base64 de `admin:password123` |

Constats :

- Le jeton est une chaîne hexadécimale courte (15 caractères observés, par exemple
  `16dd74f59f0f807`).
- La documentation n'indique ni la durée de validité du jeton, ni la façon de le révoquer.
- Les identifiants de démonstration sont publiés dans la documentation : c'est normal pour une
  API de démonstration, inacceptable en production.

## 5. Codes de retour : documentés et observés

Observations du 01/10/2026, faites sur des réservations créées pour l'occasion et supprimées
ensuite.

| # | Requête | Documenté | Observé | Corps observé | Écart |
|---|---|---|---|---|---|
| 1 | `GET /ping` | 201 | **201** | `Created` | — |
| 2 | `POST /auth` identifiants valides | 200 | **200** | `{"token":"…"}` | — |
| 3 | `POST /auth` mauvais mot de passe | non documenté | **200** | `{"reason":"Bad credentials"}` | ⚠️ 200 malgré l'échec (401 attendu) |
| 4 | `POST /auth` corps vide `{}` | non documenté | **200** | `{"reason":"Bad credentials"}` | ⚠️ idem (400 attendu) |
| 5 | `GET /booking` | 200 | **200** | tableau d'identifiants | — |
| 6 | `GET /booking?firstname=X&lastname=Y` | 200 | **200** | tableau filtré | — |
| 7 | `GET /booking?firstname=<inconnu>` | non documenté | **200** | `[]` | — (liste vide cohérente) |
| 8 | `GET /booking?checkin=date-invalide` | non documenté | **500** | `Internal Server Error` | ⚠️ erreur serveur (400 attendu) |
| 9 | `GET /booking/{id}` existant | 200 | **200** | objet `Booking` | — |
| 10 | `GET /booking/{id}` inexistant | non documenté | **404** | `Not Found` (texte brut) | — (code correct, corps non JSON) |
| 11 | `GET /booking/abc` | non documenté | **404** | `Not Found` | — |
| 12 | `POST /booking` corps valide | 200 | **200** | `{bookingid, booking}` | — (201 serait plus usuel) |
| 13 | `POST /booking` sans `firstname` | non documenté | **500** | `Internal Server Error` | ⚠️ erreur serveur (400 attendu) |
| 14 | `POST /booking` sans `bookingdates` | non documenté | **500** | `Internal Server Error` | ⚠️ idem |
| 15 | `POST /booking` sans `additionalneeds` | champ marqué obligatoire | **200** | réservation créée sans le champ | ⚠️ champ documenté obligatoire mais facultatif en pratique |
| 16 | `POST /booking` `firstname` numérique | non documenté | **500** | `Internal Server Error` | ⚠️ erreur serveur (400 attendu) |
| 17 | `POST /booking` `totalprice: "cent"` | non documenté | **200** | `"totalprice": null` | ⚠️ type invalide accepté, donnée perdue |
| 18 | `POST /booking` checkout avant checkin | non documenté | **200** | réservation créée | ⚠️ incohérence de dates acceptée |
| 19 | `POST /booking` `checkin: "pas-une-date"` | non documenté | **200** | `"checkin": "0NaN-aN-aN"` | ⚠️ date invalide acceptée et corrompue |
| 20 | `POST /booking` `totalprice: -50` | non documenté | **200** | réservation créée | ⚠️ prix négatif accepté |
| 21 | `POST /booking` JSON malformé | non documenté | **400** | `Bad Request` | — |
| 22 | `PUT` avec jeton valide (cookie) | 200 | **200** | objet mis à jour | — |
| 23 | `PUT` sans authentification | non documenté | **403** | `Forbidden` | — (accès refusé ; 401 serait plus précis) |
| 24 | `PUT` avec jeton invalide | non documenté | **403** | `Forbidden` | — |
| 25 | `PUT` sur un identifiant inexistant | non documenté | **405** | `Method Not Allowed` | ⚠️ 404 attendu |
| 26 | `PATCH` avec Basic Auth | 200 | **200** | objet complet, champ modifié | — |
| 27 | `PATCH` sans authentification | non documenté | **403** | `Forbidden` | — |
| 28 | `DELETE` sans authentification | non documenté | **403** | `Forbidden` | — |
| 29 | `DELETE` avec jeton valide | 201 | **201** | `Created` | — (conforme à la doc) |
| 30 | `GET` après suppression | non documenté | **404** | `Not Found` | — (suppression effective) |
| 31 | `DELETE` d'une réservation déjà supprimée | non documenté | **405** | `Method Not Allowed` | ⚠️ 404 attendu |

**Temps de réponse observés** : environ 0,34 s à 0,40 s par requête, mesurés depuis le poste de
test.

**Synthèse des écarts**

1. **Validation des entrées absente ou défaillante.** Selon le champ, une donnée invalide
   provoque soit une erreur serveur 500, soit une création silencieuse avec des données
   corrompues (`null`, `0NaN-aN-aN`).
2. **Codes HTTP non standard** : 200 sur un échec d'authentification, 405 sur une ressource
   inexistante.
3. **Règles métier non contrôlées** : dates incohérentes et prix négatif acceptés.
4. **Contrôle d'accès effectif** : aucune modification ni suppression n'a été possible sans
   authentification valide.

## 6. Remarques sur la documentation elle-même

Ces points ont été relevés en lisant la documentation officielle :

| # | Constat |
|---|---|
| D1 | Les exemples `curl` de `PATCH /booking/{id}` utilisent `-X PUT` au lieu de `-X PATCH`. |
| D2 | Les réponses de `GET /ping` et `DELETE` sont classées sous le titre « Success 200 », alors que le code décrit est `201 Created`. |
| D3 | Pour `PATCH`, l'en-tête `Cookie` est décrit comme donnant accès « au endpoint PUT ». |
| D4 | Aucun code d'erreur n'est documenté (400, 403, 404, 405, 500), sur aucun endpoint. |
| D5 | La description de l'identifiant de `DELETE` indique « l'ID de la réservation à mettre à jour ». |
| D6 | Le type de l'identifiant varie : `Number` pour PUT, PATCH et DELETE, `String` pour GET. |

## 7. Parcours nominal : diagramme de séquence

```mermaid
sequenceDiagram
    autonumber
    actor C as Consommateur (front / partenaire / admin)
    participant API as API Restful Booker

    C->>API: POST /auth {username, password}
    API-->>C: 200 OK {token}
    Note over C: Le jeton est conservé pour les opérations protégées

    C->>API: POST /booking {firstname, lastname, totalprice, depositpaid, bookingdates, additionalneeds}
    API-->>C: 200 OK {bookingid, booking}
    Note over C: Le bookingid est conservé

    C->>API: GET /booking/{bookingid}
    API-->>C: 200 OK {booking}

    C->>API: PUT /booking/{bookingid} + Cookie: token=… {booking complet}
    API-->>C: 200 OK {booking modifié}

    C->>API: DELETE /booking/{bookingid} + Cookie: token=…
    API-->>C: 201 Created

    C->>API: GET /booking/{bookingid}
    API-->>C: 404 Not Found
```
