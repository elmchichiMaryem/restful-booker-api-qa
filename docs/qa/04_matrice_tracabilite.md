# Matrice de traçabilité — API Restful Booker

Cette matrice relie chaque exigence (user story) à sa vérification, à travers toute la chaîne :

**US** (besoin) → **CT** (cas de test manuel) → **test Postman** (dossier › requête) →
**test pytest** (fichier::test[paramètre]) → **anomalie** (BUG-xx).

| Élément | Valeur |
|---|---|
| Date de mise à jour | 02/10/2026 |
| Sources | [User stories](../ba/03_user_stories.md) · [Cas de test](02_cas_de_test.md) · [Anomalies](03_rapports_anomalies.md) · [Collection Postman](../../postman/restful-booker.postman_collection.json) · [Tests pytest](../../tests/) |
| Méthode | Matrice extraite automatiquement des références CT présentes dans les descriptions des requêtes Postman et dans les identifiants et docstrings des tests pytest, puis relue |

**Statut manuel** : ✅ conforme · ❌ non conforme (anomalie). Dans les suites automatisées, un CT
❌ correspond à un test marqué « anomalie connue » : préfixe `[BUG-xx]` dans Postman, `xfail`
strict dans pytest.

---

## 1. Couverture par user story

| US | Titre | MoSCoW | CT | CT conformes | CT automatisés Postman | CT automatisés pytest | Anomalies |
|---|---|---|---|---|---|---|---|
| US-01 | Vérifier la disponibilité de l'API | Must | 1 | 1 | 1 | 1 | — |
| US-02 | Obtenir un jeton d'authentification | Must | 4 | 1 | 3 | 4 | BUG-01 |
| US-03 | Créer une réservation | Must | 17 | 2 | 13 | 17 | BUG-02 à BUG-10 |
| US-04 | Consulter une réservation | Must | 2 | 2 | 2 | 2 | — |
| US-05 | Lister les réservations | Should | 1 | 1 | 1 | 1 | — |
| US-06 | Rechercher par nom du client | Should | 3 | 3 | 3 | 3 | — |
| US-07 | Rechercher par dates de séjour | Could | 7 | 3 | 7 | 7 | BUG-11, BUG-12, BUG-13 |
| US-08 | Modifier entièrement une réservation | Must | 4 | 3 | 4 | 4 | BUG-14 |
| US-09 | Modifier partiellement une réservation | Should | 3 | 1 | 3 | 3 | BUG-05, BUG-14 |
| US-10 | Supprimer une réservation | Must | 3 | 2 | 3 | 3 | BUG-14 |
| US-11 | Protéger les opérations sensibles | Must | 7 | 7 | 7 | 7 | — |
| US-12 | Recevoir des erreurs claires | Should | 1 | 1 | 1 | 1 | BUG-02, BUG-11 (via RG-18) |
| **Total** | | | **53** | **27** | **48** | **53** | **14** |

- **100 % des user stories** sont couvertes par au moins un cas de test, et **100 % des CT** sont
  automatisés en pytest.
- **Postman automatise 48 CT sur 53.** Les 5 restants (CT-05, CT-09, CT-10, CT-11, CT-18) sont des
  variantes d'un même contrôle (champ manquant, dates égales). La collection n'en garde qu'un
  échantillon représentatif, alors que pytest les couvre toutes par paramétrage.
- **Toute anomalie est rattachée à au moins un CT, une US et un test automatisé.** Si elle est
  corrigée, le test correspondant le signale : XPASS en pytest, échec explicite en Postman.

## 2. Matrice détaillée

| US | CT | Manuel | Test Postman | Test pytest | Anomalie |
|---|---|---|---|---|---|
| US-01 | CT-01 | ✅ | Authentification › Vérifier la disponibilité de l'API | `test_disponibilite_auth.py::test_ping_api_disponible` | — |
| US-02 | CT-02 | ✅ | Authentification › Créer un jeton d'authentification | `test_contrat.py::test_contrat_creation_jeton`<br>`test_disponibilite_auth.py::test_jeton_delivre_avec_identifiants_valides` | — |
| US-02 | CT-03 | ❌ | Cas négatifs › [BUG-01] Jeton — mot de passe incorrect | `test_disponibilite_auth.py::test_aucun_jeton_sans_identifiants_valides[CT-03-mot-de-passe-incorrect]`<br>`test_disponibilite_auth.py::test_code_http_echec_authentification[CT-03-mot-de-passe-incorrect]` | BUG-01 |
| US-02 | CT-04 | ❌ | Cas négatifs › [BUG-01] Jeton — corps vide | `test_disponibilite_auth.py::test_aucun_jeton_sans_identifiants_valides[CT-04-corps-vide]`<br>`test_disponibilite_auth.py::test_code_http_echec_authentification[CT-04-corps-vide]` | BUG-01 |
| US-02 | CT-05 | ❌ | — (couvert par pytest) | `test_disponibilite_auth.py::test_aucun_jeton_sans_identifiants_valides[CT-05-sans-mot-de-passe]`<br>`test_disponibilite_auth.py::test_code_http_echec_authentification[CT-05-sans-mot-de-passe]` | BUG-01 |
| US-03 | CT-06 | ✅ | Réservations — CRUD › Créer une réservation | `test_contrat.py::test_contrat_creation_reservation`<br>`test_reservations_crud.py::test_creer_reservation` | — |
| US-03 | CT-07 | ✅ | Réservations — CRUD › Lire la réservation créée | `test_reservations_crud.py::test_lire_reservation` | — |
| US-03 | CT-08 | ❌ | Cas négatifs › [BUG-02] Création — sans firstname | `test_validation_creation.py::test_creation_refusee_si_champ_obligatoire_absent[CT-08-sans-firstname]` | BUG-02 |
| US-03 | CT-09 | ❌ | — (couvert par pytest) | `test_validation_creation.py::test_creation_refusee_si_champ_obligatoire_absent[CT-09-sans-lastname]` | BUG-02 |
| US-03 | CT-10 | ❌ | — (couvert par pytest) | `test_validation_creation.py::test_creation_refusee_si_champ_obligatoire_absent[CT-10-sans-totalprice]` | BUG-02 |
| US-03 | CT-11 | ❌ | — (couvert par pytest) | `test_validation_creation.py::test_creation_refusee_si_champ_obligatoire_absent[CT-11-sans-depositpaid]` | BUG-02 |
| US-03 | CT-12 | ❌ | Cas négatifs › [BUG-02] Création — sans bookingdates | `test_validation_creation.py::test_creation_refusee_si_champ_obligatoire_absent[CT-12-sans-bookingdates]` | BUG-02 |
| US-03 | CT-13 | ❌ | Cas négatifs › [BUG-10] Création — sans additionalneeds | `test_validation_creation.py::test_creation_refusee_si_champ_obligatoire_absent[CT-13-sans-additionalneeds]` | BUG-10 |
| US-03 | CT-14 | ❌ | Cas négatifs › [BUG-03] Création — totalprice non numérique | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-14-totalprice-texte]` | BUG-03 |
| US-03 | CT-15 | ❌ | Cas négatifs › [BUG-02] Création — firstname numérique | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-15-firstname-numerique]` | BUG-02 |
| US-03 | CT-16 | ❌ | Cas négatifs › [BUG-04] Création — depositpaid en chaîne "false" | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-16-depositpaid-chaine-false]` | BUG-04 |
| US-03 | CT-17 | ❌ | Cas négatifs › [BUG-05] Création — départ avant l'arrivée | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-17-depart-avant-arrivee]` | BUG-05 |
| US-03 | CT-18 | ❌ | — (couvert par pytest) | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-18-depart-egal-arrivee]` | BUG-05 |
| US-03 | CT-19 | ❌ | Cas négatifs › [BUG-06] Création — date au format invalide | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-19-date-non-valide]` | BUG-06 |
| US-03 | CT-20 | ❌ | Cas négatifs › [BUG-07] Création — date inexistante (30 février) | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-20-date-inexistante-30-fevrier]` | BUG-07 |
| US-03 | CT-21 | ❌ | Cas négatifs › [BUG-08] Création — prix négatif | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-21-prix-negatif]` | BUG-08 |
| US-03 | CT-22 | ❌ | Cas négatifs › [BUG-09] Création — prénom vide | `test_validation_creation.py::test_creation_refusee_si_valeur_invalide[CT-22-prenom-vide]` | BUG-09 |
| US-04 | CT-24 | ✅ | Réservations — CRUD › Lire la réservation créée | `test_contrat.py::test_contrat_lecture_reservation`<br>`test_reservations_crud.py::test_lire_reservation` | — |
| US-04 | CT-25 | ✅ | Cas négatifs › Lecture — réservation inexistante | `test_reservations_crud.py::test_lire_reservation_inexistante` | — |
| US-05 | CT-26 | ✅ | Réservations — CRUD › Lister les réservations | `test_contrat.py::test_contrat_liste_reservations`<br>`test_reservations_crud.py::test_lister_reservations` | — |
| US-06 | CT-27 | ✅ | Filtres › Filtrer par prénom et nom | `test_filtres.py::test_filtrer_par_prenom_et_nom` | — |
| US-06 | CT-28 | ✅ | Filtres › Filtrer par prénom | `test_filtres.py::test_filtrer_par_prenom` | — |
| US-06 | CT-29 | ✅ | Filtres › Filtrer par un prénom inexistant | `test_filtres.py::test_filtrer_par_prenom_inexistant` | — |
| US-07 | CT-30 | ❌ | Filtres › [BUG-12] Filtrer par date d'arrivée — jour de l'arrivée | `test_filtres.py::test_filtrer_par_dates[CT-30-checkin-jour-arrivee]` | BUG-12 |
| US-07 | CT-31 | ✅ | Filtres › Filtrer par date d'arrivée — veille de l'arrivée | `test_filtres.py::test_filtrer_par_dates[CT-31-checkin-veille-arrivee]` | — |
| US-07 | CT-32 | ✅ | Filtres › Filtrer par date de départ — jour du départ | `test_filtres.py::test_filtrer_par_dates[CT-32-checkout-jour-depart]` | — |
| US-07 | CT-33 | ❌ | Cas négatifs › [BUG-11] Recherche — date d'arrivée invalide | `test_filtres.py::test_filtrer_avec_date_invalide` | BUG-11 |
| US-07 | CT-51 | ❌ | Filtres › [BUG-13] Filtrer par date de départ — veille du départ | `test_filtres.py::test_filtrer_par_dates[CT-51-checkout-veille-depart]` | BUG-13 |
| US-07 | CT-52 | ❌ | Filtres › [BUG-13] Filtrer par date de départ — lendemain du départ | `test_filtres.py::test_filtrer_par_dates[CT-52-checkout-lendemain-depart]` | BUG-13 |
| US-07 | CT-53 | ✅ | Filtres › Filtrer par date d'arrivée — lendemain de l'arrivée | `test_filtres.py::test_filtrer_par_dates[CT-53-checkin-lendemain-arrivee]` | — |
| US-08 | CT-34 | ✅ | Réservations — CRUD › Modifier entièrement la réservation (jeton) | `test_reservations_crud.py::test_modifier_entierement_reservation` | — |
| US-08 | CT-35 | ✅ | Réservations — CRUD › Modifier entièrement la réservation (Basic Auth) | `test_reservations_crud.py::test_modifier_entierement_reservation` | — |
| US-08 | CT-36 | ❌ | Cas négatifs › [BUG-14] Modification — PUT sur une réservation inexistante | `test_reservations_crud.py::test_operation_sur_reservation_inexistante[CT-36-put]` | BUG-14 |
| US-08 | CT-37 | ✅ | Cas négatifs › Modification — PUT avec corps incomplet | `test_reservations_crud.py::test_modifier_avec_corps_incomplet_refuse` | — |
| US-09 | CT-38 | ✅ | Réservations — CRUD › Modifier partiellement la réservation (PATCH) | `test_reservations_crud.py::test_modifier_partiellement_reservation` | — |
| US-09 | CT-39 | ❌ | Cas négatifs › [BUG-14] Modification partielle — PATCH sur une réservation inexistante | `test_reservations_crud.py::test_operation_sur_reservation_inexistante[CT-39-patch]` | BUG-14 |
| US-09 | CT-40 | ❌ | Cas négatifs › [BUG-05] Modification partielle — départ avant l'arrivée | `test_reservations_crud.py::test_modifier_partiellement_dates_incoherentes_refuse` | BUG-05 |
| US-10 | CT-48 | ✅ | Réservations — CRUD › Supprimer la réservation (jeton)<br>Réservations — CRUD › Vérifier que la réservation supprimée est introuvable | `test_reservations_crud.py::test_supprimer_reservation` | — |
| US-10 | CT-49 | ❌ | Cas négatifs › [BUG-14] Suppression — réservation inexistante | `test_reservations_crud.py::test_supprimer_reservation_deja_supprimee` | BUG-14 |
| US-10 | CT-50 | ✅ | Réservations — CRUD › Supprimer la réservation (Basic Auth) | `test_reservations_crud.py::test_supprimer_reservation` | — |
| US-11 | CT-41 | ✅ | Cas négatifs › Sécurité — PUT sans authentification | `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[CT-41-put-sans-auth]` | — |
| US-11 | CT-42 | ✅ | Cas négatifs › Sécurité — PUT avec un jeton invalide | `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[CT-42-put-jeton-invalide]` | — |
| US-11 | CT-43 | ✅ | Cas négatifs › Sécurité — PUT avec Basic Auth invalide | `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[CT-43-put-basic-invalide]` | — |
| US-11 | CT-44 | ✅ | Cas négatifs › Sécurité — PATCH sans authentification | `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[CT-44-patch-sans-auth]` | — |
| US-11 | CT-45 | ✅ | Cas négatifs › Sécurité — PATCH avec un jeton invalide | `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[CT-45-patch-jeton-invalide]` | — |
| US-11 | CT-46 | ✅ | Cas négatifs › Sécurité — DELETE sans authentification | `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[CT-46-delete-sans-auth]` | — |
| US-11 | CT-47 | ✅ | Cas négatifs › Sécurité — DELETE avec un jeton invalide | `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[CT-47-delete-jeton-invalide]` | — |
| US-12 | CT-23 | ✅ | Cas négatifs › Création — JSON mal formé | `test_validation_creation.py::test_creation_refusee_si_json_mal_forme` | — |

## 3. Tests automatisés hors cas de test manuels

Ces tests complètent la couverture au-delà des 53 CT :

| Test | Rôle | Exigence |
|---|---|---|
| `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[complement-patch-basic-invalide]` | Matrice de sécurité complète : PATCH avec Basic Auth invalide | US-11, RG-09 |
| `test_securite.py::test_operation_protegee_refusee_sans_authentification_valide[complement-delete-basic-invalide]` | Matrice de sécurité complète : DELETE avec Basic Auth invalide | US-11, RG-09 |
| `test_reservations_crud.py::test_operation_sur_reservation_inexistante[delete-identifiant-inexistant]` | DELETE sur un identifiant qui n'a jamais existé (BUG-14) | US-10, RG-13 |
| `test_contrat.py::test_schema_detecte_une_reponse_non_conforme` | Contrôle du dispositif : le schéma rejette bien une réservation corrompue | Contrat |
| Postman : test commun « Temps de réponse < seuil » | Exécuté sur chaque requête de la collection | Performance (indicatif) |
| Postman : `Réservations — CRUD › Relire la réservation modifiée` | Persistance des modifications PUT et PATCH | US-08, US-09 |

## 4. Anomalies et tests associés

| Anomalie | Sévérité | CT | Postman | pytest |
|---|---|---|---|---|
| BUG-01 | Mineure | CT-03 à CT-05 | 2 requêtes `[BUG-01]` | `test_code_http_echec_authentification` (3 cas xfail) |
| BUG-02 | Majeure | CT-08 à CT-12, CT-15 | 3 requêtes `[BUG-02]` | `test_creation_refusee_si_champ_obligatoire_absent` (5 cas) + `test_creation_refusee_si_valeur_invalide[CT-15…]` |
| BUG-03 | Majeure | CT-14 | 1 requête | `test_creation_refusee_si_valeur_invalide[CT-14…]` |
| BUG-04 | Majeure | CT-16 | 1 requête | `test_creation_refusee_si_valeur_invalide[CT-16…]` |
| BUG-05 | Majeure | CT-17, CT-18, CT-40 | 2 requêtes | `test_creation_refusee_si_valeur_invalide[CT-17…, CT-18…]` + `test_modifier_partiellement_dates_incoherentes_refuse` |
| BUG-06 | Majeure | CT-19 | 1 requête | `test_creation_refusee_si_valeur_invalide[CT-19…]` |
| BUG-07 | Majeure | CT-20 | 1 requête | `test_creation_refusee_si_valeur_invalide[CT-20…]` |
| BUG-08 | Majeure | CT-21 | 1 requête | `test_creation_refusee_si_valeur_invalide[CT-21…]` |
| BUG-09 | Mineure | CT-22 | 1 requête | `test_creation_refusee_si_valeur_invalide[CT-22…]` |
| BUG-10 | Mineure | CT-13 | 1 requête | `test_creation_refusee_si_champ_obligatoire_absent[CT-13…]` |
| BUG-11 | Mineure | CT-33 | 1 requête | `test_filtrer_avec_date_invalide` |
| BUG-12 | Majeure | CT-30 | 1 requête | `test_filtrer_par_dates[CT-30…]` |
| BUG-13 | Majeure | CT-51, CT-52 | 2 requêtes | `test_filtrer_par_dates[CT-51…, CT-52…]` |
| BUG-14 | Mineure | CT-36, CT-39, CT-49 | 3 requêtes | `test_operation_sur_reservation_inexistante` (3 cas) + `test_supprimer_reservation_deja_supprimee` |
