# Cas de test — API Restful Booker

| Élément | Valeur |
|---|---|
| Date d'exécution | 01/10/2026 |
| Environnement | https://restful-booker.herokuapp.com (public, partagé) |
| Exécutante | Maryem Elmchichi |
| Mode d'exécution | Manuel, assisté par script (requêtes réelles, une pause de 0,4 s entre chaque requête) |
| Données | Réservations créées pour la campagne (prénom suffixé d'un identifiant aléatoire), toutes supprimées en fin d'exécution |

**Conventions**

- **Type** : `P` = positif (comportement nominal) · `N` = négatif (entrée invalide ou accès refusé).
- **Priorité** : Haute / Moyenne / Basse, selon la priorité MoSCoW de l'US et le risque couvert.
- **Résultat attendu** : issu de la documentation ou des règles de gestion. Ce n'est jamais le
  comportement observé (voir la [stratégie](01_strategie_de_test.md) §4.1).
- **Statut** : ✅ conforme · ❌ non conforme (anomalie associée).
- **Données de référence** (notées `réservation valide`) :

```json
{
  "firstname": "Qa<id>", "lastname": "Campagne<id>", "totalprice": 150, "depositpaid": true,
  "bookingdates": { "checkin": "2026-11-01", "checkout": "2026-11-05" },
  "additionalneeds": "Petit-déjeuner"
}
```

---

## 1. Synthèse d'exécution

| Indicateur | Valeur |
|---|---|
| Cas de test | 53 |
| Exécutés | 53 (100 %) |
| Conformes ✅ | 27 (50,9 %) |
| Non conformes ❌ | 26 (49,1 %) |
| Cas positifs / négatifs | 17 / 36 |
| Anomalies ouvertes | 14 (BUG-01 à BUG-14) |

| Domaine | Cas | ✅ | ❌ |
|---|---|---|---|
| Disponibilité et authentification | CT-01 à CT-05 | 2 | 3 |
| Création | CT-06 à CT-23 | 3 | 15 |
| Lecture | CT-24 à CT-26 | 3 | 0 |
| Recherche (filtres) | CT-27 à CT-33, CT-51 à CT-53 | 6 | 4 |
| Modification | CT-34 à CT-40 | 4 | 3 |
| Sécurité (contrôle d'accès) | CT-41 à CT-47 | 7 | 0 |
| Suppression | CT-48 à CT-50 | 2 | 1 |

**Lecture rapide** : le parcours nominal et le contrôle d'accès sont **entièrement conformes**.
Les échecs portent sur la **validation des données**, le **choix des codes HTTP** et les
**filtres de dates**.

---

## 2. Disponibilité et authentification

| ID | US | RG | Endpoint | Méthode | Données | Résultat attendu | Prio. | Type | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|---|---|---|---|
| CT-01 | US-01 | RG-15 | `/ping` | GET | — | 201 `Created` | Haute | P | 201 `Created` | ✅ |
| CT-02 | US-02 | RG-10 | `/auth` | POST | `{"username":"admin","password":"password123"}` | 200, `token` chaîne non vide | Haute | P | 200 `{"token":"22b08a69265a260"}` | ✅ |
| CT-03 | US-02 | RG-11 | `/auth` | POST | mot de passe `mauvais` | 401, pas de `token` | Haute | N | 200 `{"reason":"Bad credentials"}` | ❌ BUG-01 |
| CT-04 | US-02 | RG-11 | `/auth` | POST | corps `{}` | 400, pas de `token` | Moyenne | N | 200 `{"reason":"Bad credentials"}` | ❌ BUG-01 |
| CT-05 | US-02 | RG-11 | `/auth` | POST | `{"username":"admin"}` (sans mot de passe) | 400, pas de `token` | Moyenne | N | 200 `{"reason":"Bad credentials"}` | ❌ BUG-01 |

## 3. Création d'une réservation — `POST /booking`

| ID | US | RG | Données | Résultat attendu | Prio. | Type | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|---|---|
| CT-06 | US-03 | RG-14 | réservation valide | 200, `bookingid` entier, `booking` identique aux données envoyées | Haute | P | 200, `bookingid` 556, `booking` identique | ✅ |
| CT-07 | US-03 | RG-14 | `GET /booking/{id}` après CT-06 | 200, données identiques à la création | Haute | P | 200, données identiques | ✅ |
| CT-08 | US-03 | RG-01 | réservation valide sans `firstname` | 400, aucune création | Haute | N | 500 `Internal Server Error` | ❌ BUG-02 |
| CT-09 | US-03 | RG-01 | sans `lastname` | 400, aucune création | Haute | N | 500 `Internal Server Error` | ❌ BUG-02 |
| CT-10 | US-03 | RG-01 | sans `totalprice` | 400, aucune création | Haute | N | 500 `Internal Server Error` | ❌ BUG-02 |
| CT-11 | US-03 | RG-01 | sans `depositpaid` | 400, aucune création | Haute | N | 500 `Internal Server Error` | ❌ BUG-02 |
| CT-12 | US-03 | RG-01 | sans `bookingdates` | 400, aucune création | Haute | N | 500 `Internal Server Error` | ❌ BUG-02 |
| CT-13 | US-03 | RG-01 | sans `additionalneeds` | 400 (champ documenté obligatoire) | Basse | N | 200, réservation créée sans le champ | ❌ BUG-10 |
| CT-14 | US-03 | RG-03 | `"totalprice": "cent"` | 400 | Haute | N | 200, `"totalprice": null` enregistré | ❌ BUG-03 |
| CT-15 | US-03 | RG-02 | `"firstname": 123` | 400 | Moyenne | N | 500 `Internal Server Error` | ❌ BUG-02 |
| CT-16 | US-03 | RG-05 | `"depositpaid": "oui"` | 400 | Haute | N | 200, `"depositpaid": true` enregistré | ❌ BUG-04 |
| CT-17 | US-03 | RG-07 | checkin `2026-11-10`, checkout `2026-11-01` | 400, aucune création | Haute | N | 200, réservation créée | ❌ BUG-05 |
| CT-18 | US-03 | RG-07 | checkin = checkout = `2026-11-10` | 400 (séjour d'au moins une nuit) | Moyenne | N | 200, réservation créée | ❌ BUG-05 |
| CT-19 | US-03 | RG-06 | `"checkin": "pas-une-date"` | 400 | Haute | N | 200, `"checkin": "0NaN-aN-aN"` enregistré | ❌ BUG-06 |
| CT-20 | US-03 | RG-06 | `"checkin": "2026-02-30"` (date inexistante) | 400 | Moyenne | N | 200, `"checkin": "2026-03-02"` enregistré | ❌ BUG-07 |
| CT-21 | US-03 | RG-04 | `"totalprice": -50` | 400 | Moyenne | N | 200, réservation créée à −50 | ❌ BUG-08 |
| CT-22 | US-03 | RG-02 | `"firstname": ""` | 400 | Basse | N | 200, réservation créée sans prénom | ❌ BUG-09 |
| CT-23 | US-12 | RG-18 | JSON mal formé `{"firstname": "Qa",` | 400 | Moyenne | N | 400 `Bad Request` | ✅ |

## 4. Lecture

| ID | US | RG | Endpoint | Méthode | Données | Résultat attendu | Prio. | Type | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|---|---|---|---|
| CT-24 | US-04 | — | `/booking/{id}` | GET | réservation existante, `Accept: application/json` | 200, corps conforme au schéma `Booking` (6 champs, types corrects) | Haute | P | 200, schéma conforme | ✅ |
| CT-25 | US-04 | RG-13 | `/booking/999999999` | GET | identifiant inexistant | 404 | Haute | N | 404 `Not Found` | ✅ |
| CT-26 | US-05 | — | `/booking` | GET | — | 200, tableau de `{bookingid}` contenant l'id créé | Moyenne | P | 200, 469 identifiants, id présent | ✅ |

## 5. Recherche (filtres) — `GET /booking`

Les filtres de dates sont combinés au prénom unique de la campagne, pour ne dépendre d'aucune
donnée tierce. La réservation de référence va du **01/11/2026 au 05/11/2026**.

| ID | US | RG | Paramètres | Résultat attendu | Prio. | Type | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|---|---|
| CT-27 | US-06 | RG-16 | `firstname=<unique>&lastname=<unique>` | 200, contient l'id | Haute | P | 200, id présent | ✅ |
| CT-28 | US-06 | RG-16 | `firstname=<unique>` | 200, contient l'id | Moyenne | P | 200, id présent | ✅ |
| CT-29 | US-06 | RG-16 | `firstname=Inexistant<id>` | 200, `[]` | Moyenne | N | 200 `[]` | ✅ |
| CT-30 | US-07 | RG-17 | `checkin=2026-11-01` (égal à l'arrivée) | 200, contient l'id (≥) | Moyenne | P | 200, id **absent** | ❌ BUG-12 |
| CT-31 | US-07 | RG-17 | `checkin=2026-10-31` (veille de l'arrivée) | 200, contient l'id | Moyenne | P | 200, id présent | ✅ |
| CT-32 | US-07 | RG-17 | `checkout=2026-11-05` (égal au départ) | 200, contient l'id (≥) | Moyenne | P | 200, id présent | ✅ |
| CT-33 | US-07 | RG-17, RG-18 | `checkin=date-invalide` | 400 | Basse | N | 500 `Internal Server Error` | ❌ BUG-11 |
| CT-51 | US-07 | RG-17 | `checkout=2026-11-04` (veille du départ) | 200, contient l'id (05/11 ≥ 04/11) | Moyenne | P | 200, id **absent** | ❌ BUG-13 |
| CT-52 | US-07 | RG-17 | `checkout=2026-11-06` (lendemain du départ) | 200, ne contient pas l'id (05/11 < 06/11) | Moyenne | N | 200, id **présent** | ❌ BUG-13 |
| CT-53 | US-07 | RG-17 | `checkin=2026-11-02` (lendemain de l'arrivée) | 200, ne contient pas l'id (01/11 < 02/11) | Moyenne | N | 200, id absent | ✅ |

## 6. Modification

| ID | US | RG | Endpoint | Méthode | Données | Résultat attendu | Prio. | Type | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|---|---|---|---|
| CT-34 | US-08 | RG-09, RG-10 | `/booking/{id}` | PUT | réservation complète modifiée + `Cookie: token=<valide>` | 200, nouvelles valeurs, persistées à la relecture | Haute | P | 200, valeurs modifiées et persistées | ✅ |
| CT-35 | US-08 | RG-10 | `/booking/{id}` | PUT | réservation complète + `Authorization: Basic` valide | 200, nouvelles valeurs | Haute | P | 200, valeurs modifiées | ✅ |
| CT-36 | US-08 | RG-13 | `/booking/999999999` | PUT | réservation valide + jeton valide | 404 | Moyenne | N | 405 `Method Not Allowed` | ❌ BUG-14 |
| CT-37 | US-08 | RG-01 | `/booking/{id}` | PUT | réservation sans `lastname` + jeton valide | 400 | Moyenne | N | 400 `Bad Request` | ✅ |
| CT-38 | US-09 | RG-08 | `/booking/{id}` | PATCH | `{"additionalneeds":"Vue sur mer"}` + jeton valide | 200, seul `additionalneeds` modifié | Haute | P | 200, seul le champ ciblé modifié | ✅ |
| CT-39 | US-09 | RG-13 | `/booking/999999999` | PATCH | `{"firstname":"X"}` + jeton valide | 404 | Basse | N | 405 `Method Not Allowed` | ❌ BUG-14 |
| CT-40 | US-09 | RG-07, RG-08 | `/booking/{id}` | PATCH | `bookingdates` checkin `2026-11-10`, checkout `2026-11-01` + jeton valide | 400, réservation inchangée | Moyenne | N | 200, dates incohérentes enregistrées | ❌ BUG-05 |

## 7. Sécurité — contrôle d'accès

Pour chaque cas, une relecture (`GET`) vérifie que la réservation est **inchangée**.

| ID | US | RG | Méthode | Authentification envoyée | Résultat attendu | Prio. | Type | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|---|---|---|
| CT-41 | US-11 | RG-09 | PUT | aucune | 403, réservation inchangée | Haute | N | 403 `Forbidden`, inchangée | ✅ |
| CT-42 | US-11 | RG-09 | PUT | `Cookie: token=invalide123` | 403, réservation inchangée | Haute | N | 403 `Forbidden`, inchangée | ✅ |
| CT-43 | US-11 | RG-09 | PUT | `Authorization: Basic` de `admin:mauvais` | 403, réservation inchangée | Haute | N | 403 `Forbidden`, inchangée | ✅ |
| CT-44 | US-11 | RG-09 | PATCH | aucune | 403, réservation inchangée | Haute | N | 403 `Forbidden`, inchangée | ✅ |
| CT-45 | US-11 | RG-09 | PATCH | `Cookie: token=invalide123` | 403, réservation inchangée | Haute | N | 403 `Forbidden`, inchangée | ✅ |
| CT-46 | US-11 | RG-09 | DELETE | aucune | 403, réservation toujours présente | Haute | N | 403 `Forbidden`, présente | ✅ |
| CT-47 | US-11 | RG-09 | DELETE | `Cookie: token=invalide123` | 403, réservation toujours présente | Haute | N | 403 `Forbidden`, présente | ✅ |

## 8. Suppression — `DELETE /booking/{id}`

| ID | US | RG | Données | Résultat attendu | Prio. | Type | Résultat obtenu | Statut |
|---|---|---|---|---|---|---|---|---|
| CT-48 | US-10 | RG-09, RG-12 | réservation existante + jeton valide | 201, puis `GET` → 404 | Haute | P | 201 `Created`, puis 404 | ✅ |
| CT-49 | US-10 | RG-13 | réservation déjà supprimée + jeton valide | 404 | Basse | N | 405 `Method Not Allowed` | ❌ BUG-14 |
| CT-50 | US-10 | RG-10, RG-12 | réservation existante + `Authorization: Basic` valide | 201, puis `GET` → 404 | Haute | P | 201 `Created`, puis 404 | ✅ |

---

## 9. Notes d'exploration

Sessions exploratoires menées en complément des cas écrits. Chaque constat a été rejoué sur des
données dédiées, supprimées ensuite.

1. **Sémantique réelle des filtres de dates.** Deux réservations au même prénom unique ont été
   créées : A du 01/11 au 05/11 et C du 01/11 au 20/11.

   | Filtre | A | C | Interprétation |
   |---|---|---|---|
   | `checkin=2026-10-31` | ✔ | ✔ | |
   | `checkin=2026-11-01` | ✘ | ✘ | L'égalité est exclue : le filtre applique `checkin > D` |
   | `checkin=2026-11-02` | ✘ | ✘ | |
   | `checkout=2026-11-04` | ✘ | ✘ | |
   | `checkout=2026-11-05` | ✔ | ✘ | Le filtre renvoie les départs ≤ D, l'inverse du ≥ documenté |
   | `checkout=2026-11-10` | ✔ | ✘ | |
   | `checkout=2026-11-20` | ✔ | ✔ | |

   Ces résultats ont donné naissance aux cas CT-51 à CT-53 et aux anomalies BUG-12 et BUG-13.

2. **Conversion silencieuse de `depositpaid`.** Avec `"oui"`, `"non"` et `"false"` (chaînes),
   l'API enregistre `true` ; avec `0`, elle enregistre `false`. Toute chaîne non vide devient
   donc `true`, y compris `"false"` : le sens de la donnée est inversé (BUG-04).

3. **Dates normalisées.** Une date inexistante est convertie au lieu d'être refusée (30 février →
   2 mars, BUG-07). Une chaîne non datable devient `0NaN-aN-aN` (BUG-06).

4. **Comportements conformes à la documentation mais non usuels**, notés sans anomalie :
   `DELETE` renvoie 201 au lieu de 200/204 ; `POST /booking` renvoie 200 au lieu de 201 ;
   l'accès refusé renvoie 403 même sans authentification, alors que 401 serait plus précis ;
   les corps d'erreur sont en texte brut (`Not Found`, `Forbidden`) et non en JSON.

5. **Temps de réponse** : entre 88 et 94 ms sur l'ensemble de la campagne, mesurés depuis le
   poste de test. Ils sont nettement plus bas qu'en Phase 1 (~350 ms), ce qui montre la
   variabilité de l'API partagée.
