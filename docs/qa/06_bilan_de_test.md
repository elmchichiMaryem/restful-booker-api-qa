# Bilan de test — API Restful Booker

| Élément | Valeur |
|---|---|
| Version | 1.0 |
| Date | 05/10/2026 |
| Auteure | Maryem Elmchichi |
| Période de test | du 01/10/2026 au 05/10/2026 |
| Environnement | https://restful-booker.herokuapp.com (public, partagé) |
| Références | [Stratégie](01_strategie_de_test.md) · [Cas de test](02_cas_de_test.md) · [Anomalies](03_rapports_anomalies.md) · [Traçabilité](04_matrice_tracabilite.md) · [Performance](05_rapport_performance.md) |

---

## 1. Synthèse

L'API Restful Booker **remplit son parcours nominal** : créer, lire, lister, modifier et
supprimer une réservation fonctionne. Son **contrôle d'accès est fiable** : aucune modification
ni suppression n'a été possible sans authentification valide. Ses **temps de réponse sont bons**
sous charge légère.

En revanche, elle **ne valide pas les données reçues**. Une donnée invalide provoque soit une
erreur serveur, soit, plus grave, une réservation enregistrée avec des données corrompues ou au
sens inversé. **Deux filtres de recherche par date** ne respectent pas la documentation.

| Indicateur clé | Valeur |
|---|---|
| Cas de test exécutés | **53 / 53 (100 %)** |
| Taux de conformité | **27 / 53 (50,9 %)** |
| Anomalies | **14** : 0 bloquante · 0 critique · 9 majeures · 5 mineures |
| User stories couvertes | **12 / 12 (100 %)** ; 5 entièrement conformes |
| Automatisation | 53 CT automatisés en pytest, 48 en Postman ; suites vertes |
| Performance | Tous les seuils respectés (p95 : 90 ms unitaire, 182 à 270 ms liste ; 0 % d'erreur) |

**Avis QA** : l'API est **conforme pour le parcours nominal et la sécurité d'accès**, mais **non
prête pour une mise en production** tant que les 6 anomalies de priorité haute ne sont pas
corrigées. La plupart relèvent d'une même cause : l'absence de validation des entrées.

## 2. Exécution des tests

### 2.1 Campagne manuelle (Phase 2)

| Domaine | Cas | ✅ Conformes | ❌ Non conformes | Taux |
|---|---|---|---|---|
| Disponibilité et authentification | 5 | 2 | 3 | 40 % |
| Création | 18 | 3 | 15 | 17 % |
| Lecture | 3 | 3 | 0 | 100 % |
| Recherche (filtres) | 10 | 6 | 4 | 60 % |
| Modification | 7 | 4 | 3 | 57 % |
| Sécurité (contrôle d'accès) | 7 | 7 | 0 | **100 %** |
| Suppression | 3 | 2 | 1 | 67 % |
| **Total** | **53** | **27** | **26** | **50,9 %** |

| Type de cas | Nombre | Conformes |
|---|---|---|
| Positifs (nominal) | 17 | 14 (82 %) |
| Négatifs (entrées invalides, accès refusé) | 36 | 13 (36 %) |

Les cas positifs en échec sont tous des filtres de dates (BUG-12, BUG-13). Le faible taux des
cas négatifs reflète l'absence de validation : l'API accepte ce qu'elle devrait refuser.

### 2.2 Suites automatisées

| Suite | Contenu | Résultat |
|---|---|---|
| **pytest** | 64 tests (6 modules) | **37 réussis · 27 anomalies connues (xfail strict) · 0 échec** |
| **Postman / Newman** | 54 requêtes, 179 assertions | **179 / 179 assertions réussies · 0 échec** (21 requêtes `[BUG-xx]`) |
| **k6** | 124 requêtes, 5 VU, 30 s | **5 / 5 seuils respectés**, 0 % d'erreur, 217 / 217 vérifications |

« Réussi » signifie, pour une anomalie connue, que **l'anomalie est toujours présente** :
le test vérifie le comportement attendu et le signalerait s'il devenait conforme. Une suite
verte signifie donc qu'aucune régression ni aucune évolution non documentée n'a été détectée.

| Marqueur pytest | Tests |
|---|---|
| `smoke` | 9 |
| `contrat` | 10 |
| `securite` | 15 |
| `regression` | 64 |

### 2.3 Intégration continue

Le workflow GitHub Actions exécute pytest puis Newman à chaque push et à chaque pull request
sur `main`, et publie les deux rapports HTML en artefacts. Le test k6 se lance manuellement
(`workflow_dispatch`).

Résultats des premières exécutions (05/10/2026) :

| Exécution | Déclencheur | pytest | Newman | k6 | Durée | Statut |
|---|---|---|---|---|---|---|
| [37316348996](https://github.com/elmchichiMaryem/restful-booker-api-qa/actions/runs/37316348996) | push | 37 réussis · 27 xfail | 179 / 179 | non lancé (prévu) | 1 min 49 s | ✅ |
| [37316655044](https://github.com/elmchichiMaryem/restful-booker-api-qa/actions/runs/37316655044) | manuel | 37 réussis · 27 xfail | 179 / 179 | 5 / 5 seuils, 0 % d'erreur | — | ✅ |

Aucune relance n'a été nécessaire. Les trois rapports (`rapport-pytest`, `rapport-newman`,
`rapport-k6`) sont publiés en artefacts.

## 3. Anomalies

### 3.1 Par sévérité et priorité

| Sévérité \ Priorité | Haute | Moyenne | Basse | Total |
|---|---|---|---|---|
| Bloquante | 0 | 0 | 0 | **0** |
| Critique | 0 | 0 | 0 | **0** |
| Majeure | 6 | 3 | 0 | **9** |
| Mineure | 0 | 2 | 3 | **5** |
| **Total** | **6** | **5** | **3** | **14** |

### 3.2 Par cause

| Cause | Anomalies | Nombre |
|---|---|---|
| Absence de validation des entrées | BUG-02, BUG-03, BUG-04, BUG-05, BUG-06, BUG-07, BUG-08, BUG-09, BUG-11 | 9 |
| Logique des filtres de dates | BUG-12, BUG-13 | 2 |
| Codes HTTP inadaptés | BUG-01, BUG-14 | 2 |
| Écart entre documentation et implémentation | BUG-10 | 1 |

### 3.3 Anomalies prioritaires (priorité haute)

| ID | Titre | Risque métier |
|---|---|---|
| BUG-02 | Champ obligatoire manquant ou nom de type incorrect → 500 | Le consommateur ne peut pas distinguer son erreur d'une panne |
| BUG-03 | Prix non numérique enregistré à `null` | Réservation sans prix |
| BUG-04 | `depositpaid: "false"` enregistré `true` | **Acompte non payé enregistré comme payé** |
| BUG-05 | Date de départ antérieure ou égale à l'arrivée acceptée | Séjours impossibles, facturation faussée |
| BUG-06 | Date invalide enregistrée `0NaN-aN-aN` | Donnée corrompue renvoyée à tous les consommateurs |
| BUG-13 | Filtre `checkout` inversé | Les partenaires obtiennent l'inverse du résultat attendu |

Toutes les anomalies sont reproductibles, avec une commande `curl` rejouée et vérifiée (voir les
[rapports d'anomalies](03_rapports_anomalies.md)).

## 4. Couverture des exigences

| US | Titre | MoSCoW | CT | Conformes | Statut |
|---|---|---|---|---|---|
| US-01 | Vérifier la disponibilité de l'API | Must | 1 | 1 | ✅ Conforme |
| US-02 | Obtenir un jeton d'authentification | Must | 4 | 1 | ⚠️ Partiel (BUG-01) |
| US-03 | Créer une réservation | Must | 17 | 2 | ❌ Validation absente (BUG-02 à BUG-10) |
| US-04 | Consulter une réservation | Must | 2 | 2 | ✅ Conforme |
| US-05 | Lister les réservations | Should | 1 | 1 | ✅ Conforme (pagination recommandée) |
| US-06 | Rechercher par nom du client | Should | 3 | 3 | ✅ Conforme |
| US-07 | Rechercher par dates de séjour | Could | 7 | 3 | ❌ Filtres incorrects (BUG-11 à BUG-13) |
| US-08 | Modifier entièrement une réservation | Must | 4 | 3 | ⚠️ Partiel (BUG-14) |
| US-09 | Modifier partiellement une réservation | Should | 3 | 1 | ⚠️ Partiel (BUG-05, BUG-14) |
| US-10 | Supprimer une réservation | Must | 3 | 2 | ⚠️ Partiel (BUG-14) |
| US-11 | Protéger les opérations sensibles | Must | 7 | 7 | ✅ Conforme |
| US-12 | Recevoir des erreurs claires | Should | 1 | 1 | ⚠️ Conforme sur son CT, mais BUG-02 et BUG-11 contredisent RG-18 |

- **Couverture** : 12 US sur 12 couvertes par au moins un cas de test, et les 7 US *Must* le
  sont toutes.
- **Conformité** : 5 US entièrement conformes (US-01, 04, 05, 06, 11), 5 partiellement
  conformes et 2 non conformes.

Le détail US → CT → Postman → pytest → anomalie figure dans la
[matrice de traçabilité](04_matrice_tracabilite.md).

## 5. Critères de sortie

Rappel des critères de la [stratégie de test](01_strategie_de_test.md) §6.2 :

| Critère | Résultat | Statut |
|---|---|---|
| 100 % des cas de test exécutés | 53 / 53 | ✅ |
| 100 % des US *Must* couvertes | 7 / 7 | ✅ |
| Chaque cas en échec rattaché à une anomalie reproductible | 26 / 26 rattachés à BUG-01 à BUG-14 | ✅ |
| Aucune anomalie bloquante ou critique ouverte sans décision | 0 bloquante, 0 critique | ✅ |
| Suites automatisées vertes (anomalies connues marquées) | pytest, Newman et k6 verts | ✅ |
| Seuils de performance respectés | 5 / 5 | ✅ |

**Les critères de sortie de la campagne de test sont atteints.** La campagne est close. Cela ne
préjuge pas de la mise en production, qui dépend de la correction des anomalies prioritaires
(§3.3).

## 6. Constats sur l'environnement de test

| Constat | Impact | Traitement |
|---|---|---|
| Réinitialisation complète de l'API toutes les quelques minutes : réservations effacées **et jetons invalidés** | Faux échecs en cascade (403) si un jeton est réutilisé après une réinitialisation (incident du 05/10/2026 : 17 échecs Newman) | Jeton frais pour chaque requête ou test protégé, nettoyage en Basic Auth, relance unique en cas d'échec |
| Liste `GET /booking` sans pagination | Temps de réponse croissant avec le volume (182 → 270 ms) | Seuil k6 avec marge ; recommandation de pagination |
| API partagée | Données de tiers imprévisibles | Données uniques par test, filtres combinés au prénom unique, suppression systématique |

## 7. Recommandations

| # | Recommandation | Anomalies traitées | Priorité |
|---|---|---|---|
| 1 | **Valider les corps de requête par schéma** à l'entrée de `POST`, `PUT` et `PATCH` (types, champs requis, format et cohérence des dates, prix ≥ 0), avec des réponses 400 explicites | BUG-02 à BUG-09 | Haute |
| 2 | **Corriger les filtres de dates** : `checkin ≥ D` et `checkout ≥ D`, conformément à la documentation | BUG-12, BUG-13 | Haute |
| 3 | **Aligner les codes HTTP sur les usages REST** : 401 en cas d'échec d'authentification, 404 pour une ressource inexistante, 400 pour un filtre invalide | BUG-01, BUG-11, BUG-14 | Moyenne |
| 4 | **Mettre à jour la documentation** : statut obligatoire de `additionalneeds`, codes d'erreur, erreurs D1 à D6 de l'analyse | BUG-10 | Basse |
| 5 | **Paginer `GET /booking`** pour maîtriser le temps de réponse | — (constat de performance) | Moyenne |
| 6 | **Après correction** : retirer les marqueurs `[BUG-xx]` et `xfail`. Les suites le signalent automatiquement : XPASS en pytest, échec explicite en Postman | — | — |
