# Rapport de performance — Charge légère (k6)

| Élément | Valeur |
|---|---|
| Date des mesures | 05/10/2026 |
| Outil | k6 v2.3.0 |
| Script | [performance/charge_legere.js](../../performance/charge_legere.js) |
| Lancement | `npm run test:perf` (rapports dans `reports/k6/`) ; en CI, déclenchement **manuel uniquement** |
| Environnement | https://restful-booker.herokuapp.com (public, partagé), depuis un poste en France |

> **Résultats indicatifs.** L'API est un environnement de démonstration gratuit, partagé par de
> nombreux utilisateurs et réinitialisé toutes les quelques minutes. Les chiffres ci-dessous
> donnent un ordre de grandeur et permettent de détecter une dégradation nette. Ce ne sont pas
> des engagements de niveau de service.

---

## 1. Objectif

- Mesurer les temps de réponse des opérations principales sous une charge **légère et
  réaliste**.
- Fixer des seuils d'acceptation justifiés par la mesure.
- Fournir un test de non-régression des performances, lançable à la demande.

L'objectif n'est **pas** de trouver la limite de l'API : un test de stress sur une API publique
partagée dégraderait le service des autres utilisateurs.

## 2. Profil de charge

| Paramètre | Valeur | Justification |
|---|---|---|
| Utilisateurs virtuels (VU) | **5 au maximum** | Plafond fixé pour respecter une API partagée |
| Durée | **30 s** : montée de 5 s, palier de 20 s, descente de 5 s | Courte, montée progressive, pas de pic brutal |
| Pause | **1 s après chaque requête** | Rythme proche d'un utilisateur réel ; limite le débit |
| Débit obtenu | **≈ 3,8 requêtes/s** (124 requêtes en 33 s) | Charge négligeable pour un serveur web |

## 3. Scénario

Chaque itération d'un utilisateur virtuel enchaîne les opérations suivantes :

| # | Requête | Rôle | Vérifications |
|---|---|---|---|
| 1 | `GET /booking` | Lire la liste des réservations | Code 200, tableau JSON |
| 2 | `POST /booking` | Créer une réservation (prénom unique) | Code 200, `bookingid` entier |
| 3 | `GET /booking/{id}` | Lire la réservation qui vient d'être créée | Code 200, prénom présent |
| 4 | `DELETE /booking/{id}` | Nettoyage, en Basic Auth (non mesuré par les seuils) | Code 201 |

**Choix de conception**

- **La lecture porte sur la réservation créée par l'itération**, et non sur un identifiant pris
  au hasard dans la liste. Une réservation tierce peut être supprimée à tout moment (autres
  utilisateurs, réinitialisations) : on mesurerait alors des erreurs 404 sans lien avec la
  performance.
- **Chaque itération supprime ses données.** Le test laisse l'API dans l'état où il l'a trouvée.
- **La configuration (URL, identifiants, réservation type) est lue dans
  [data/test_data.json](../../data/test_data.json)**, la même source que les tests pytest.
- **Chaque requête est taguée par endpoint**, ce qui permet des seuils et des statistiques
  séparés.

## 4. Démarche de définition des seuils

### 4.1 Première mesure (sans seuil de temps)

Deux exécutions consécutives ont donné des résultats concordants à 1 ms près :

| Endpoint | Requêtes | Médiane | p95 | Max |
|---|---|---|---|---|
| `GET /booking` | 31 | 179 ms | 182 ms | 186 ms |
| `POST /booking` | 31 | 89 ms | 91 ms | 93 ms |
| `GET /booking/{id}` | 31 | 89 ms | 90 ms | 92 ms |
| `DELETE /booking/{id}` (nettoyage) | 31 | 89 ms | 90 ms | 93 ms |

Taux d'erreur : **0 %** (0 sur 124).

### 4.2 Seuils retenus

| Seuil k6 | Valeur | Justification |
|---|---|---|
| `http_req_failed` | **rate < 1 %** | Exigence du projet |
| `checks` | **rate > 99 %** | Les réponses doivent aussi être fonctionnellement correctes, pas seulement rapides |
| `http_req_duration{name:GET /booking}` | **p(95) < 600 ms** | ≈ 3 × le p95 mesuré (182 ms) |
| `http_req_duration{name:GET /booking/{id}}` | **p(95) < 300 ms** | ≈ 3 × le p95 mesuré (90 ms) |
| `http_req_duration{name:POST /booking}` | **p(95) < 300 ms** | ≈ 3 × le p95 mesuré (91 ms) |

**Pourquoi une marge d'environ 3 ?**

- **Assez large** pour absorber la variabilité d'un environnement partagé. La troisième mesure
  l'illustre : le p95 de la liste est passé de 182 à 270 ms en quelques minutes (voir §5).
- **Assez serrée** pour détecter une vraie dégradation : un doublement du temps de traitement
  côté serveur resterait visible sur les opérations unitaires, qui sont très stables (écart
  min–max d'environ 5 ms).
- **Seuils distincts par endpoint.** Un seuil global unique serait dominé par la liste, plus
  lente, et masquerait une dégradation des opérations unitaires.

> **Remarque sur la Phase 1** : des temps de 340 à 400 ms y avaient été relevés avec `curl`.
> Ils ne sont pas comparables : `curl` ouvre une nouvelle connexion (DNS, TCP, TLS) à chaque
> appel, alors que k6 réutilise ses connexions comme le ferait une application cliente. Les
> ~90 ms mesurés ici correspondent essentiellement à l'aller-retour réseau entre la France et
> l'hébergement de l'API.

## 5. Résultats de l'exécution de référence

Exécution du 05/10/2026 avec les seuils actifs : **tous les seuils sont respectés.**

| Seuil | Résultat | Statut |
|---|---|---|
| `http_req_failed` < 1 % | 0,00 % (0 sur 124) | ✅ |
| `checks` > 99 % | 100 % (217 sur 217) | ✅ |
| `GET /booking` p95 < 600 ms | 269,5 ms | ✅ |
| `GET /booking/{id}` p95 < 300 ms | 89,4 ms | ✅ |
| `POST /booking` p95 < 300 ms | 90,2 ms | ✅ |

| Endpoint | Min | Médiane | p90 | p95 | p99 | Max |
|---|---|---|---|---|---|---|
| `GET /booking` | 260,0 | 265,5 | 267,8 | 269,5 | 274,4 | 275,7 |
| `POST /booking` | 87,2 | 88,9 | 89,9 | 90,2 | 90,8 | 90,9 |
| `GET /booking/{id}` | 87,1 | 88,3 | 89,1 | 89,4 | 89,7 | 89,8 |

*(valeurs en millisecondes)*

| Indicateur | Valeur |
|---|---|
| Itérations | 31 (≈ 4,5 s chacune, dont 4 s de pauses) |
| Requêtes | 124 (3,7 requêtes/s) |
| Données reçues | 1,4 Mo |

## 6. Interprétation

1. **Les opérations unitaires sont rapides et très stables** : création et lecture autour de
   89 ms, avec moins de 5 ms d'écart entre le minimum et le maximum. Le temps de traitement
   côté serveur est négligeable devant la latence réseau.
2. **La liste complète est l'opération la plus coûteuse, et son coût augmente avec le volume de
   données.** `GET /booking` renvoie **tous** les identifiants, sans pagination.

   | Mesure | Données reçues | Taille estimée de la liste | p95 de `GET /booking` |
   |---|---|---|---|
   | 1 et 2 | 1,1 Mo | ≈ 1 800 réservations (≈ 35 Ko) | 182 ms |
   | 3 | 1,4 Mo | ≈ 2 400 réservations (≈ 45 Ko) | 270 ms |
   | Contrôle ponctuel | — | 2 522 réservations (47 Ko) | — |

   Le temps de réponse augmente avec la taille de la liste. Le nombre de réservations dépend de
   l'activité des autres utilisateurs depuis la dernière réinitialisation de l'API.
3. **Aucune erreur sous charge légère** : 5 utilisateurs simultanés n'entraînent ni erreur ni
   dégradation mesurable des opérations unitaires.

### Recommandation

**Ajouter une pagination à `GET /booking`** (paramètres `page`/`limit` ou curseur). Sans
pagination, le temps de réponse et la bande passante croissent linéairement avec le nombre de
réservations. C'est un risque de performance pour un partenaire qui synchronise régulièrement la
liste complète (US-05). Il s'agit d'un **constat de conception et non d'une anomalie** : la
documentation ne promet ni pagination ni temps de réponse.

## 7. Limites

| Limite | Conséquence |
|---|---|
| API de démonstration gratuite et partagée | Les temps dépendent de l'activité des autres utilisateurs : résultats **indicatifs** |
| Réinitialisations toutes les quelques minutes (voir [l'analyse de l'API](../ba/02_analyse_api.md) §4) | Une réinitialisation pendant le test peut provoquer quelques erreurs (réservation effacée entre création et lecture) ; avec environ 124 requêtes, 2 erreurs suffisent à dépasser le seuil de 1 % |
| Taille de la liste variable | Le p95 de `GET /booking` varie d'une exécution à l'autre (182 à 270 ms observés) |
| Charge très faible (5 VU) | Ne renseigne pas sur le comportement à forte charge ni sur la capacité maximale, volontairement non testés |
| Mesure depuis un seul point (France) ; en CI, depuis l'infrastructure GitHub | La latence réseau, qui domine les temps mesurés, dépend du lieu d'exécution |
| 3 exécutions de 30 s | Échantillon réduit : 31 requêtes par endpoint et par exécution |

## 8. Exécution et rapports

```bash
npm run test:perf
```

| Rapport | Contenu |
|---|---|
| Console | Résumé k6 : seuils, vérifications, statistiques par endpoint |
| `reports/k6/rapport-k6.html` | Tableau de bord k6 exporté (graphiques de débit, latences et VU dans le temps) |
| `reports/k6/resume-k6.json` | Résumé des métriques au format JSON (exploitable par un outil) |

En intégration continue, le test k6 **ne s'exécute pas à chaque push**. Il se lance
manuellement (`workflow_dispatch`), pour ne pas imposer de charge répétée à l'API publique.
