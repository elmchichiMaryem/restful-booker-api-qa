# Rapports d'anomalies — API Restful Booker

| Élément | Valeur |
|---|---|
| Date de détection | 01/10/2026 |
| Environnement | https://restful-booker.herokuapp.com (public, partagé) |
| Détectées par | Maryem Elmchichi |
| Méthode de vérification | Chaque anomalie a été observée au moins deux fois (campagne de la Phase 2 et rejeu des commandes ci-dessous) |
| Classification | Voir la [stratégie de test](01_strategie_de_test.md) §7 |

> Toutes les commandes de reproduction s'exécutent telles quelles. Celles qui créent une
> réservation doivent être suivies de sa suppression (commande en fin de document), afin de ne
> pas polluer l'API partagée.

---

## Synthèse

| ID | Titre | Endpoint | Sévérité | Priorité | Cas de test | Règle |
|---|---|---|---|---|---|---|
| BUG-01 | Un échec d'authentification renvoie 200 au lieu de 401/400 | `POST /auth` | Mineure | Moyenne | CT-03, CT-04, CT-05 | RG-11 |
| BUG-02 | Un champ obligatoire manquant ou un nom de type incorrect provoque une erreur 500 | `POST /booking` | Majeure | Haute | CT-08 à CT-12, CT-15 | RG-01, RG-02, RG-18 |
| BUG-03 | Un prix non numérique est accepté et enregistré à `null` | `POST /booking` | Majeure | Haute | CT-14 | RG-03 |
| BUG-04 | `depositpaid` non booléen est converti : `"false"` devient `true` | `POST /booking` | Majeure | Haute | CT-16 | RG-05 |
| BUG-05 | Une date de départ antérieure ou égale à l'arrivée est acceptée | `POST`, `PATCH /booking` | Majeure | Haute | CT-17, CT-18, CT-40 | RG-07 |
| BUG-06 | Une date invalide est enregistrée sous la forme `0NaN-aN-aN` | `POST /booking` | Majeure | Haute | CT-19 | RG-06 |
| BUG-07 | Une date inexistante (30 février) est convertie silencieusement (2 mars) | `POST /booking` | Majeure | Moyenne | CT-20 | RG-06 |
| BUG-08 | Un prix négatif est accepté | `POST /booking` | Majeure | Moyenne | CT-21 | RG-04 |
| BUG-09 | Un prénom vide est accepté | `POST /booking` | Mineure | Basse | CT-22 | RG-02 |
| BUG-10 | `additionalneeds`, documenté obligatoire, est facultatif en pratique | `POST /booking` | Mineure | Basse | CT-13 | RG-01 |
| BUG-11 | Un filtre de date invalide provoque une erreur 500 | `GET /booking` | Mineure | Moyenne | CT-33 | RG-17, RG-18 |
| BUG-12 | Le filtre `checkin` exclut la date égale (> au lieu de ≥) | `GET /booking` | Majeure | Moyenne | CT-30 | RG-17 |
| BUG-13 | Le filtre `checkout` est inversé (≤ au lieu de ≥) | `GET /booking` | Majeure | Haute | CT-51, CT-52 | RG-17 |
| BUG-14 | Une opération sur une réservation inexistante renvoie 405 au lieu de 404 | `PUT`, `PATCH`, `DELETE /booking/{id}` | Mineure | Basse | CT-36, CT-39, CT-49 | RG-13 |

**Répartition par sévérité** : 0 Bloquante · 0 Critique · 9 Majeures · 5 Mineures.

**Répartition par priorité** : 6 Hautes · 5 Moyennes · 3 Basses.

**Analyse** : aucune anomalie ne touche le contrôle d'accès ni le parcours nominal. Le défaut
dominant est l'**absence de validation des entrées** (BUG-02 à BUG-10, soit 9 anomalies sur 14).
Une seule correction de fond, une validation par schéma à l'entrée de `POST`, `PUT` et `PATCH`,
traiterait l'essentiel des anomalies.

---

## BUG-01 — Un échec d'authentification renvoie 200 au lieu de 401/400

| Champ | Valeur |
|---|---|
| Endpoint | `POST /auth` |
| Sévérité | Mineure |
| Priorité | Moyenne |
| Cas de test | CT-03, CT-04, CT-05 |
| Règle | RG-11 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/auth \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"mauvais"}'
```

**Résultat attendu** : `401 Unauthorized` pour des identifiants incorrects (`400 Bad Request`
pour un corps vide ou incomplet), sans jeton.

**Résultat obtenu** : `200 OK`, corps `{"reason":"Bad credentials"}`. Le même résultat est
obtenu avec `{}` et avec `{"username":"admin"}`.

**Impact** : un consommateur qui se fie au code HTTP croit l'authentification réussie. Il doit
inspecter le corps pour détecter l'échec. Aucun jeton n'est délivré, donc il n'y a pas de faille
de sécurité.

---

## BUG-02 — Un champ obligatoire manquant ou un nom de type incorrect provoque une erreur 500

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Majeure |
| Priorité | Haute |
| Cas de test | CT-08, CT-09, CT-10, CT-11, CT-12, CT-15 |
| Règles | RG-01, RG-02, RG-18 |

**Requête pour reproduire** (exemple sans `firstname`)

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"lastname":"Bug02","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'
```

Variante avec un type incorrect :

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":123,"lastname":"Bug02","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request` avec un message indiquant le champ en cause. Aucune
réservation créée.

**Résultat obtenu** : `500 Internal Server Error`, corps `Internal Server Error`. Le même
résultat est obtenu sans `lastname`, `totalprice`, `depositpaid` ou `bookingdates`. Aucune
réservation n'est créée.

**Impact** : le consommateur ne peut pas distinguer son erreur d'une panne du serveur, ni
afficher un message utile. Les erreurs 500 faussent aussi la supervision.

---

## BUG-03 — Un prix non numérique est accepté et enregistré à `null`

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Majeure |
| Priorité | Haute |
| Cas de test | CT-14 |
| Règle | RG-03 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug03","lastname":"Prix","totalprice":"cent","depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request`, aucune réservation créée.

**Résultat obtenu** : `200 OK`, réservation créée avec `"totalprice": null`.

**Impact** : réservation enregistrée **sans prix**, donc une perte d'information financière que
le consommateur n'est pas en mesure de détecter.

---

## BUG-04 — `depositpaid` non booléen est converti : `"false"` devient `true`

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Majeure |
| Priorité | Haute |
| Cas de test | CT-16 |
| Règle | RG-05 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug04","lastname":"Acompte","totalprice":150,"depositpaid":"false","bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request`, car `depositpaid` doit être un booléen.

**Résultat obtenu** : `200 OK`, réservation créée avec `"depositpaid": true`. Les chaînes
`"oui"` et `"non"` donnent aussi `true` ; seul `0` donne `false`.

**Impact** : **le sens de la donnée est inversé**. Une réservation envoyée avec acompte « non
payé » est enregistrée comme payée, avec un risque financier direct.

---

## BUG-05 — Une date de départ antérieure ou égale à l'arrivée est acceptée

| Champ | Valeur |
|---|---|
| Endpoints | `POST /booking`, `PATCH /booking/{id}` |
| Sévérité | Majeure |
| Priorité | Haute |
| Cas de test | CT-17, CT-18, CT-40 |
| Règle | RG-07 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug05","lastname":"Dates","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-11-10","checkout":"2026-11-01"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request`, car un séjour doit se terminer après son début.

**Résultat obtenu** : `200 OK`, réservation créée du 10/11 au 01/11. Le même résultat est
obtenu avec des dates égales (CT-18) et en modification partielle (`PATCH`, CT-40).

**Impact** : réservations impossibles en base, susceptibles de fausser le planning et la
facturation (nombre de nuits négatif ou nul).

---

## BUG-06 — Une date invalide est enregistrée sous la forme `0NaN-aN-aN`

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Majeure |
| Priorité | Haute |
| Cas de test | CT-19 |
| Règle | RG-06 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug06","lastname":"Format","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"pas-une-date","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request`, format `AAAA-MM-JJ` exigé.

**Résultat obtenu** : `200 OK`, réservation créée avec `"checkin": "0NaN-aN-aN"`.

**Impact** : donnée corrompue et inexploitable, renvoyée telle quelle à tous les consommateurs.

---

## BUG-07 — Une date inexistante (30 février) est convertie silencieusement (2 mars)

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Majeure |
| Priorité | Moyenne |
| Cas de test | CT-20 |
| Règle | RG-06 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug07","lastname":"Calendrier","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-02-30","checkout":"2026-03-05"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request`, car le 30 février n'existe pas.

**Résultat obtenu** : `200 OK`, réservation créée avec `"checkin": "2026-03-02"`.

**Impact** : la réservation enregistrée ne correspond pas à la demande du client, sans qu'il en
soit averti.

---

## BUG-08 — Un prix négatif est accepté

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Majeure |
| Priorité | Moyenne |
| Cas de test | CT-21 |
| Règle | RG-04 (hypothèse métier) |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug08","lastname":"Negatif","totalprice":-50,"depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request`, car un prix ne peut pas être négatif.

**Résultat obtenu** : `200 OK`, réservation créée avec `"totalprice": -50`.

**Impact** : montants incohérents, susceptibles de se propager à la facturation.

---

## BUG-09 — Un prénom vide est accepté

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Mineure |
| Priorité | Basse |
| Cas de test | CT-22 |
| Règle | RG-02 (hypothèse métier) |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"","lastname":"Bug09","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'
```

**Résultat attendu** : `400 Bad Request`, car le client doit être identifiable.

**Résultat obtenu** : `200 OK`, réservation créée avec `"firstname": ""`.

**Impact** : réservation difficile à rattacher à un client et introuvable par le filtre
`firstname`.

---

## BUG-10 — `additionalneeds`, documenté obligatoire, est facultatif en pratique

| Champ | Valeur |
|---|---|
| Endpoint | `POST /booking` |
| Sévérité | Mineure |
| Priorité | Basse |
| Cas de test | CT-13 |
| Règle | RG-01 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug10","lastname":"Besoins","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"}}'
```

**Résultat attendu** : selon la documentation, `400 Bad Request`, car le champ est marqué
obligatoire (non optionnel).

**Résultat obtenu** : `200 OK`, réservation créée sans le champ `additionalneeds`.

**Impact** : écart entre la documentation et l'implémentation. Le comportement réel est
probablement le bon, car une demande particulière est facultative par nature. **Correction
recommandée côté documentation**, à arbitrer avec le métier. Les consommateurs doivent aussi
gérer l'absence du champ dans les réponses.

---

## BUG-11 — Un filtre de date invalide provoque une erreur 500

| Champ | Valeur |
|---|---|
| Endpoint | `GET /booking` |
| Sévérité | Mineure |
| Priorité | Moyenne |
| Cas de test | CT-33 |
| Règles | RG-17, RG-18 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' 'https://restful-booker.herokuapp.com/booking?checkin=date-invalide'
```

**Résultat attendu** : `400 Bad Request` (format `CCYY-MM-DD` exigé par la documentation).

**Résultat obtenu** : `500 Internal Server Error`.

**Impact** : erreur serveur sur une simple saisie incorrecte d'un partenaire. Lecture seule,
donc aucune donnée n'est touchée.

---

## BUG-12 — Le filtre `checkin` exclut la date égale (> au lieu de ≥)

| Champ | Valeur |
|---|---|
| Endpoint | `GET /booking?checkin=` |
| Sévérité | Majeure |
| Priorité | Moyenne |
| Cas de test | CT-30 |
| Règle | RG-17 |

**Requête pour reproduire**

```bash
# 1. Créer une réservation arrivant le 01/11/2026 (noter le bookingid renvoyé)
curl -s -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug12Filtre","lastname":"Checkin","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'

# 2. Filtrer sur la date d'arrivée exacte
curl -s -w '\nHTTP %{http_code}\n' 'https://restful-booker.herokuapp.com/booking?firstname=Bug12Filtre&checkin=2026-11-01'
```

**Résultat attendu** : la réservation est renvoyée, car la documentation annonce les
réservations dont la date d'arrivée est « greater than or equal to » la date fournie.

**Résultat obtenu** : `200 OK` et `[]`. La réservation n'apparaît qu'avec `checkin=2026-10-31` :
le filtre applique une comparaison **strictement supérieure**.

**Impact** : un partenaire qui cherche les arrivées à partir d'une date manque toutes celles du
jour même.

---

## BUG-13 — Le filtre `checkout` est inversé (≤ au lieu de ≥)

| Champ | Valeur |
|---|---|
| Endpoint | `GET /booking?checkout=` |
| Sévérité | Majeure |
| Priorité | Haute |
| Cas de test | CT-51, CT-52 |
| Règle | RG-17 |

**Requête pour reproduire**

```bash
# 1. Créer une réservation partant le 05/11/2026 (noter le bookingid renvoyé)
curl -s -X POST https://restful-booker.herokuapp.com/booking \
  -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Bug13Filtre","lastname":"Checkout","totalprice":150,"depositpaid":true,"bookingdates":{"checkin":"2026-11-01","checkout":"2026-11-05"},"additionalneeds":"Aucun"}'

# 2. Départ la veille : la réservation devrait apparaître (05/11 ≥ 04/11)
curl -s -w '\nHTTP %{http_code}\n' 'https://restful-booker.herokuapp.com/booking?firstname=Bug13Filtre&checkout=2026-11-04'

# 3. Départ le lendemain : la réservation ne devrait pas apparaître (05/11 < 06/11)
curl -s -w '\nHTTP %{http_code}\n' 'https://restful-booker.herokuapp.com/booking?firstname=Bug13Filtre&checkout=2026-11-06'
```

**Résultat attendu** : réservations dont la date de départ est **supérieure ou égale** à la date
fournie. L'étape 2 renvoie donc la réservation et l'étape 3 ne la renvoie pas.

**Résultat obtenu** : c'est l'inverse. L'étape 2 renvoie `[]` et l'étape 3 renvoie la
réservation. Le filtre sélectionne les départs **inférieurs ou égaux** à la date.

**Impact** : le filtre renvoie l'inverse du résultat attendu, et les intégrations partenaires
qui s'y fient obtiennent des données fausses.

---

## BUG-14 — Une opération sur une réservation inexistante renvoie 405 au lieu de 404

| Champ | Valeur |
|---|---|
| Endpoints | `PUT`, `PATCH`, `DELETE /booking/{id}` |
| Sévérité | Mineure |
| Priorité | Basse |
| Cas de test | CT-36, CT-39, CT-49 |
| Règle | RG-13 |

**Requête pour reproduire**

```bash
curl -s -w '\nHTTP %{http_code}\n' -X DELETE https://restful-booker.herokuapp.com/booking/999999999 \
  -H 'Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM='
```

**Résultat attendu** : `404 Not Found`, car la ressource n'existe pas.

**Résultat obtenu** : `405 Method Not Allowed`. Le même résultat est obtenu avec `PUT` et
`PATCH`, et avec un `DELETE` sur une réservation déjà supprimée.

**Impact** : le code 405 laisse croire que la méthode n'est pas supportée par l'endpoint. Le
consommateur ne peut pas distinguer « réservation inexistante » de « opération interdite ». Par
cohérence, `GET` sur le même identifiant renvoie bien 404.

---

## Remarques hors anomalies

Ces points sont conformes à la documentation, ou ne relèvent pas du comportement de l'API. Ils
sont signalés pour information :

- **Choix de codes HTTP discutables mais documentés** : `DELETE` renvoie `201 Created` ;
  `POST /booking` renvoie `200` au lieu de `201`.
- **Accès refusé** : il renvoie `403` même sans authentification, alors que `401` serait plus
  précis.
- **Corps d'erreur** : ils sont en texte brut (`Not Found`, `Forbidden`) et non en JSON.
- **Défauts de la documentation** : ils sont relevés en §6 de
  [l'analyse de l'API](../ba/02_analyse_api.md) (D1 à D6), par exemple des exemples `PATCH`
  écrits avec `-X PUT` et aucun code d'erreur documenté.

## Nettoyage après reproduction

```bash
curl -s -w '\nHTTP %{http_code}\n' -X DELETE https://restful-booker.herokuapp.com/booking/<bookingid> \
  -H 'Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM='
```
