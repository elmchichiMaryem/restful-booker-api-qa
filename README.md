# Restful Booker — Projet de test d'API

[![Tests de l'API Restful Booker](https://github.com/elmchichiMaryem/restful-booker-api-qa/actions/workflows/tests.yml/badge.svg)](https://github.com/elmchichiMaryem/restful-booker-api-qa/actions/workflows/tests.yml)

Projet portfolio de **recette complète d'une API REST**, de l'analyse métier jusqu'à
l'intégration continue. Il porte sur [Restful Booker](https://restful-booker.herokuapp.com), une
API publique de réservation d'hôtel ([documentation](https://restful-booker.herokuapp.com/apidoc/index.html)).

Le projet suit la démarche d'une équipe produit. On commence par **comprendre le besoin**
(Business Analyst), puis on **conçoit et exécute les tests** (QA). On **automatise** ensuite
avec Postman/Newman et pytest, on **mesure les performances** avec k6, et on **intègre le tout en
CI** avec GitHub Actions.

> Toutes les anomalies documentées ont été **observées et rejouées sur l'API réelle**. Aucune
> n'est supposée.

---

## Résultats en bref

| Indicateur | Résultat |
|---|---|
| Cas de test conçus et exécutés | **53** (17 positifs, 36 négatifs), 100 % exécutés |
| Conformité | 27 / 53 (50,9 %) |
| Anomalies documentées | **14** : 0 bloquante · 0 critique · 9 majeures · 5 mineures |
| Couverture des user stories | 12 / 12 (100 %) |
| Suite pytest | 64 tests : 37 réussis + 27 anomalies connues (`xfail` strict) |
| Collection Postman | 54 requêtes, 179 assertions, toutes réussies |
| Performance (k6, 5 VU, 30 s) | 0 % d'erreur ; p95 ≈ 90 ms (opérations unitaires), 182 à 270 ms (liste) |

**Principaux constats** : le parcours nominal et le contrôle d'accès sont fiables. En revanche,
l'API **ne valide pas ses entrées** : par exemple, `"depositpaid": "false"` est enregistré `true`
et une date invalide devient `0NaN-aN-aN`. Ses **filtres de dates** ne respectent pas la
documentation. Voir le [bilan de test](docs/qa/06_bilan_de_test.md).

## Compétences démontrées

| Domaine | Mise en œuvre dans le projet |
|---|---|
| **Analyse métier (BA)** | Note de cadrage, user stories avec critères d'acceptation Gherkin, priorisation MoSCoW, story points, règles de gestion |
| **Analyse d'API** | Inventaire des endpoints, comparaison entre comportement documenté et observé (31 observations), diagramme de séquence Mermaid |
| **OpenAPI 3** | Spécification de l'API documentée, validée avec Redocly CLI |
| **Conception de tests** | Stratégie de test, partitions d'équivalence, valeurs limites, tests de sécurité d'accès, tests exploratoires |
| **Gestion des anomalies** | 14 rapports reproductibles (commande `curl`), sévérité et priorité distinctes, analyse des causes |
| **Postman / Newman** | Collection chaînée (variables de jeton et d'identifiant), tests `pm.test`, validation de schéma, rapport htmlextra |
| **pytest + requests** | Client API réutilisable, fixtures de données isolées, tests paramétrés pilotés par les données, marqueurs, `xfail` strict |
| **JSON Schema** | Tests de contrat avec `jsonschema` (références entre schémas, contrôle du format `date`) |
| **k6** | Test de charge légère, seuils par endpoint justifiés par la mesure, rapport HTML |
| **CI/CD** | GitHub Actions : tests à chaque push et pull request, k6 manuel, rapports publiés en artefacts |
| **Traçabilité** | Matrice US → CT → test Postman → test pytest → anomalie |

## Structure du dépôt

```
restful-booker-api-qa/
├── docs/
│   ├── ba/                     Analyse métier (cadrage, analyse d'API, user stories, règles de gestion)
│   ├── api/openapi.yaml        Spécification OpenAPI 3
│   └── qa/                     Stratégie, cas de test, anomalies, traçabilité, performance, bilan
├── postman/                    Collection et environnement Postman (v2.1)
├── tests/
│   ├── clients/                Client API réutilisable et chargement de la configuration
│   ├── schemas/                Schémas JSON (tests de contrat)
│   ├── conftest.py             Fixtures (client, jeton, données isolées, rapport HTML)
│   ├── outils.py               Validation de schéma, catalogue des anomalies connues
│   └── test_*.py               Tests pytest
├── performance/charge_legere.js  Script k6
├── data/test_data.json         Configuration et jeux de données (source unique)
├── .github/workflows/tests.yml Intégration continue
├── pytest.ini · requirements.txt · package.json
```

## Lancer les tests

### Prérequis

Python 3.13, Node.js 24 ou plus, et [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/)
pour le test de performance.

```bash
git clone https://github.com/elmchichiMaryem/restful-booker-api-qa.git
cd restful-booker-api-qa

# Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Node (Newman)
npm ci
```

### Commandes

| Commande | Effet | Rapport |
|---|---|---|
| `pytest` | Suite complète (64 tests) | `reports/pytest/rapport-pytest.html` |
| `pytest -m smoke` | Parcours critiques uniquement (9 tests, environ 10 s) | idem |
| `pytest -m "contrat or securite"` | Tests de contrat et de sécurité | idem |
| `npm run test:postman` | Collection Postman avec Newman | `reports/newman/rapport-newman.html` |
| `npm run test:perf` | Charge légère k6 (5 VU, 30 s) | `reports/k6/rapport-k6.html` |

Les marqueurs pytest disponibles sont `smoke`, `regression`, `contrat` et `securite`.

Pour cibler un autre environnement, définir les variables `BOOKER_BASE_URL`, `BOOKER_USERNAME` et
`BOOKER_PASSWORD`. Elles remplacent les valeurs de `data/test_data.json`.

### Utiliser la collection dans Postman

1. Cliquer sur **Import** et sélectionner les deux fichiers du dossier `postman/`.
2. Choisir l'environnement **Restful Booker — Démo**.
3. Sur la collection, ouvrir le menu **⋯**, choisir **Run collection** et garder l'ordre des
   requêtes.

## Intégration continue

Le workflow [`.github/workflows/tests.yml`](.github/workflows/tests.yml) :

- s'exécute **à chaque push et à chaque pull request sur `main`** : vérification de
  disponibilité de l'API, **pytest**, puis **Newman** (lancé même si pytest échoue) ;
- publie les rapports HTML en **artefacts** (`rapport-pytest`, `rapport-newman`) ;
- ne lance le **test k6** qu'**à la demande**, via l'onglet *Actions* puis *Run workflow*. Il
  produit l'artefact `rapport-k6` et évite d'imposer une charge répétée à une API publique.

## Choix techniques notables

- **Anomalies connues testées sur le comportement attendu.** Dans pytest, elles sont marquées
  `xfail(strict=True)` avec leur référence `BUG-xx`. Dans Postman, les tests portent le nom
  `[BUG-xx — anomalie connue]`. Si une anomalie est corrigée, la suite échoue volontairement, ce
  qui oblige à retirer le marquage : une évolution ne passe pas inaperçue.
- **Données isolées.** Chaque test crée ses données avec un prénom unique et les supprime. Les
  réservations créées à tort par l'API lors des cas négatifs sont nettoyées aussi.
- **Robustesse à un environnement instable.** L'API publique se réinitialise toutes les quelques
  minutes : réservations effacées et jetons invalidés. Les suites utilisent donc un jeton frais
  par requête ou par test protégé, nettoient leurs données en Basic Auth et relancent une seule
  fois un test en échec. Une vraie anomalie, déterministe, échoue aussi à la relance.
- **Respect d'une API partagée.** Les pauses entre requêtes sont systématiques, la charge k6 est
  plafonnée et le test de performance n'est lancé que manuellement.

## Documentation

| Analyse métier | Assurance qualité |
|---|---|
| [Note de cadrage](docs/ba/01_note_de_cadrage.md) | [Stratégie de test](docs/qa/01_strategie_de_test.md) |
| [Analyse de l'API](docs/ba/02_analyse_api.md) | [Cas de test](docs/qa/02_cas_de_test.md) |
| [User stories](docs/ba/03_user_stories.md) | [Rapports d'anomalies](docs/qa/03_rapports_anomalies.md) |
| [Règles de gestion](docs/ba/04_regles_de_gestion.md) | [Matrice de traçabilité](docs/qa/04_matrice_tracabilite.md) |
| [Spécification OpenAPI](docs/api/openapi.yaml) | [Rapport de performance](docs/qa/05_rapport_performance.md) |
| | [Bilan de test](docs/qa/06_bilan_de_test.md) |

## Auteure

**Maryem Elmchichi** — [github.com/elmchichiMaryem](https://github.com/elmchichiMaryem)
