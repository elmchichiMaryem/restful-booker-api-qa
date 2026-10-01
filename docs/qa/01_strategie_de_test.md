# Stratégie de test — API Restful Booker

| Élément | Valeur |
|---|---|
| Version | 1.0 |
| Date | 01/10/2026 |
| Auteure | Maryem Elmchichi |
| Références | [Note de cadrage](../ba/01_note_de_cadrage.md) · [Analyse de l'API](../ba/02_analyse_api.md) · [User stories](../ba/03_user_stories.md) · [Règles de gestion](../ba/04_regles_de_gestion.md) · [OpenAPI](../api/openapi.yaml) |

---

## 1. Objectif

Vérifier que l'API Restful Booker répond aux user stories US-01 à US-12 et respecte les règles
de gestion RG-01 à RG-18. Il s'agit aussi de détecter et documenter tout écart entre la
documentation, le comportement réel et le besoin métier.

## 2. Périmètre

| Dans le périmètre | Hors périmètre |
|---|---|
| Les 8 endpoints : `/ping`, `/auth`, `/booking` (GET, POST), `/booking/{id}` (GET, PUT, PATCH, DELETE) | Formats XML et URL-encoded |
| Filtres `firstname`, `lastname`, `checkin`, `checkout` | Charge élevée, stress, endurance |
| Authentification par jeton (cookie) et Basic Auth | Tests d'intrusion, injection, fuzzing |
| Format JSON | Base de données et code source (boîte noire) |

## 3. Types de tests

| Type | Objectif | Techniques | Outils | Phase |
|---|---|---|---|---|
| **Fonctionnel positif** | Le parcours nominal fonctionne | Parcours CRUD de bout en bout, vérification de persistance par relecture | curl, Postman, pytest | 2, 3, 4 |
| **Fonctionnel négatif** | Les entrées invalides sont rejetées proprement | Partitions d'équivalence (valide, absent, mauvais type), valeurs limites (dates égales, 30 février, prix négatif) | curl, Postman, pytest | 2, 3, 4 |
| **Sécurité de base** | Les opérations protégées refusent les accès non autorisés | Matrice méthode × type d'authentification (absente, jeton invalide, mauvais identifiants), vérification que la donnée est inchangée | Postman, pytest | 2, 3, 4 |
| **Contrat** | La structure et les types des réponses sont stables | Validation par schéma JSON (champs requis, types, absence de champs inattendus) | Postman (`tv4`/`ajv`), jsonschema | 3, 4 |
| **Performance** | Donner une indication des temps de réponse sous charge légère | Charge légère plafonnée : 5 utilisateurs virtuels pendant 30 s, avec des pauses | k6 | 5 |
| **Exploratoire** | Découvrir des comportements non prévus par les cas écrits | Sessions ciblées (filtres de dates, coercition des types) | curl, script Python | 2 |
| **Non-régression** | Détecter toute évolution du comportement | Exécution automatique des suites à chaque push | GitHub Actions | 6 |

## 4. Approche

### 4.1 Base de l'attendu (oracle de test)

Le résultat attendu de chaque cas de test est déterminé dans cet ordre :

1. la **documentation officielle** quand elle est explicite ;
2. les **règles de gestion** ([04_regles_de_gestion.md](../ba/04_regles_de_gestion.md)) quand elle est
   muette (bonne pratique REST ou hypothèse métier) ;
3. on ne retient **jamais** le comportement observé comme attendu : sinon un défaut serait validé
   comme normal.

### 4.2 Gestion des données de test

- Chaque test **crée ses propres données** : prénom suffixé d'un identifiant aléatoire, pour les
  distinguer des données des autres utilisateurs de l'API publique.
- Chaque réservation créée est **supprimée en fin de test**, y compris celles créées à tort par
  l'API lors des cas négatifs.
- Les filtres sont combinés au prénom unique pour ne dépendre d'aucune donnée tierce.
- Aucune dépendance aux identifiants existants : l'API est réinitialisée régulièrement.

### 4.3 Traitement des anomalies connues dans l'automatisation

Les tests automatisés vérifient le **comportement attendu**. Une anomalie connue fait donc
échouer son test, qui est marqué explicitement : nom suffixé `[BUG-xx]` dans Postman,
`xfail(strict=True)` dans pytest. Si l'anomalie est corrigée, le test `xfail` strict passe en
« XPASS », ce qui fait échouer la suite et oblige à retirer le marquage : la correction ne
passe pas inaperçue.

## 5. Environnement

| Élément | Valeur |
|---|---|
| URL | `https://restful-booker.herokuapp.com` (environnement public unique, partagé) |
| Identifiants | `admin` / `password123` (identifiants de démonstration publiés) |
| Poste de test | macOS, Python 3.13, Node 26, Newman 6.2, k6 2.3 |
| Intégration continue | GitHub Actions (`ubuntu-latest`) |

## 6. Critères d'entrée et de sortie

### 6.1 Critères d'entrée

- `GET /ping` renvoie 201 (API disponible).
- `POST /auth` délivre un jeton avec les identifiants de démonstration.
- User stories et règles de gestion rédigées.
- Jeux de données de test préparés.

### 6.2 Critères de sortie

- 100 % des cas de test exécutés.
- 100 % des user stories *Must* couvertes par au moins un cas de test.
- Chaque cas en échec est rattaché à une anomalie documentée et reproductible (BUG-xx).
- Aucune anomalie de sévérité **Bloquante** ou **Critique** ouverte sans décision explicite.
- Suites automatisées vertes : les anomalies connues y sont marquées et les autres tests
  réussissent.
- Seuils de performance respectés, à titre indicatif.

### 6.3 Critères de suspension

- API indisponible (`/ping` en échec) ou taux d'erreurs 5xx généralisé sur le parcours nominal.
- Réinitialisation de la base pendant une campagne : la campagne est relancée.

## 7. Classification des anomalies

| Sévérité | Définition |
|---|---|
| **Bloquante** | Empêche une fonction principale, sans contournement possible |
| **Critique** | Faille de sécurité ou perte ou corruption de données à grande échelle |
| **Majeure** | Fonction incorrecte ou données corrompues, avec contournement possible |
| **Mineure** | Écart de conformité (code HTTP, documentation) sans impact sur les données |

| Priorité | Définition |
|---|---|
| **Haute** | À corriger dans la prochaine version |
| **Moyenne** | À planifier |
| **Basse** | À corriger si l'occasion se présente |

La **sévérité** mesure l'impact technique. La **priorité** mesure l'urgence métier.

## 8. Risques liés au test

| Risque | Mesure |
|---|---|
| Données modifiées par d'autres utilisateurs | Données uniques et isolées, vérification par relecture |
| API lente au réveil (hébergement gratuit) | Délai d'attente de 30 s, appel `/ping` préalable |
| Surcharge de l'API partagée | Pauses entre requêtes, k6 plafonné à 5 utilisateurs virtuels pendant 30 s et déclenché manuellement |
| Faux positifs dus à l'environnement | Toute anomalie est rejouée au moins deux fois avant d'être documentée |

## 9. Livrables QA

| Livrable | Fichier |
|---|---|
| Stratégie de test | ce document |
| Cas de test et résultats d'exécution | [02_cas_de_test.md](02_cas_de_test.md) |
| Rapports d'anomalies | [03_rapports_anomalies.md](03_rapports_anomalies.md) |
| Matrice de traçabilité | `04_matrice_tracabilite.md` (Phase 4) |
| Rapport de performance | `05_rapport_performance.md` (Phase 5) |
| Bilan de test | `06_bilan_de_test.md` (Phase 6) |
