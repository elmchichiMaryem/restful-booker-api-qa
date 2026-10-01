# User stories — API Restful Booker

Les user stories sont écrites du point de vue des **consommateurs de l'API**, c'est-à-dire des
systèmes et des personnes qui l'appellent :

| Persona | Description |
|---|---|
| **Application front** | Site web ou application mobile qui crée et affiche les réservations des clients |
| **Partenaire** | Agence de voyage ou comparateur qui recherche et consulte des réservations par intégration |
| **Administrateur** | Utilisateur du back-office hôtelier, autorisé à modifier et supprimer les réservations |
| **Équipe d'exploitation** | Supervise la disponibilité du service |

**Priorité MoSCoW** : *Must* (indispensable), *Should* (important), *Could* (souhaitable),
*Won't* (exclu de cette version).

**Story points** : estimation relative de l'effort de test, sur l'échelle de Fibonacci
(1, 2, 3, 5, 8).

Les critères d'acceptation sont rédigés en **Gherkin français** (`# language: fr`). Ils
décrivent le comportement **attendu** : documenté, ou issu des règles de gestion
([04_regles_de_gestion.md](04_regles_de_gestion.md)) quand la documentation est muette.

---

## Synthèse

| ID | Titre | Persona | MoSCoW | Points | Règles liées |
|---|---|---|---|---|---|
| US-01 | Vérifier la disponibilité de l'API | Équipe d'exploitation | Must | 1 | RG-15 |
| US-02 | Obtenir un jeton d'authentification | Administrateur | Must | 2 | RG-10, RG-11 |
| US-03 | Créer une réservation | Application front | Must | 5 | RG-01 à RG-07, RG-14 |
| US-04 | Consulter une réservation | Application front | Must | 2 | RG-13 |
| US-05 | Lister les réservations | Partenaire | Should | 1 | — |
| US-06 | Rechercher des réservations par nom du client | Partenaire | Should | 3 | RG-16 |
| US-07 | Rechercher des réservations par dates de séjour | Partenaire | Could | 3 | RG-17 |
| US-08 | Modifier entièrement une réservation | Administrateur | Must | 3 | RG-01 à RG-07, RG-09 |
| US-09 | Modifier partiellement une réservation | Administrateur | Should | 3 | RG-08, RG-09 |
| US-10 | Supprimer une réservation | Administrateur | Must | 2 | RG-09, RG-12 |
| US-11 | Protéger les opérations sensibles | Administrateur | Must | 5 | RG-09, RG-10 |
| US-12 | Recevoir des erreurs claires en cas de requête invalide | Application front | Should | 5 | RG-18 |
| | **Total** | | | **35** | |

Répartition MoSCoW : 7 *Must*, 4 *Should*, 1 *Could*.

---

## US-01 — Vérifier la disponibilité de l'API

**En tant qu'** équipe d'exploitation,
**je veux** interroger un point de contrôle de santé,
**afin de** savoir si l'API est disponible avant d'y envoyer du trafic.

**Priorité** : Must · **Points** : 1

```gherkin
# language: fr
Fonctionnalité: Contrôle de santé de l'API

  Scénario: L'API est disponible
    Quand j'envoie une requête GET sur /ping
    Alors le code de réponse est 201
    Et la réponse arrive en moins de 2 secondes
```

---

## US-02 — Obtenir un jeton d'authentification

**En tant qu'** administrateur,
**je veux** échanger mes identifiants contre un jeton,
**afin de** pouvoir effectuer les opérations protégées sans renvoyer mon mot de passe à chaque
requête.

**Priorité** : Must · **Points** : 2

```gherkin
# language: fr
Fonctionnalité: Authentification par jeton

  Scénario: Identifiants valides
    Étant donné les identifiants "admin" / "password123"
    Quand j'envoie une requête POST sur /auth avec ces identifiants
    Alors le code de réponse est 200
    Et le corps contient un champ "token" non vide de type chaîne

  Scénario: Mot de passe incorrect
    Étant donné les identifiants "admin" / "mauvais"
    Quand j'envoie une requête POST sur /auth avec ces identifiants
    Alors aucun jeton n'est renvoyé
    Et le code de réponse est 401

  Plan du scénario: Identifiants incomplets
    Quand j'envoie une requête POST sur /auth avec le corps <corps>
    Alors aucun jeton n'est renvoyé
    Et le code de réponse est 400

    Exemples:
      | corps                     |
      | {}                        |
      | {"username": "admin"}     |
      | {"password": "password123"} |
```

---

## US-03 — Créer une réservation

**En tant qu'** application front,
**je veux** enregistrer la réservation d'un client,
**afin de** lui confirmer son séjour avec un numéro de réservation.

**Priorité** : Must · **Points** : 5

```gherkin
# language: fr
Fonctionnalité: Création d'une réservation

  Scénario: Création avec des données valides
    Étant donné une réservation valide pour "Jim Brown" du "2026-11-01" au "2026-11-05"
    Quand j'envoie une requête POST sur /booking avec cette réservation
    Alors le code de réponse est 200
    Et le corps contient un "bookingid" entier
    Et le corps contient la réservation avec des valeurs identiques à celles envoyées

  Scénario: La réservation créée est consultable
    Étant donné que j'ai créé une réservation valide
    Quand j'envoie une requête GET sur /booking/{bookingid}
    Alors le code de réponse est 200
    Et les données correspondent à celles envoyées à la création

  Plan du scénario: Champ obligatoire manquant
    Étant donné une réservation valide dont le champ <champ> est absent
    Quand j'envoie une requête POST sur /booking avec cette réservation
    Alors le code de réponse est 400
    Et aucune réservation n'est créée

    Exemples:
      | champ           |
      | firstname       |
      | lastname        |
      | totalprice      |
      | depositpaid     |
      | bookingdates    |
      | additionalneeds |

  Scénario: Dates de séjour incohérentes
    Étant donné une réservation dont la date de départ "2026-11-01" précède la date d'arrivée "2026-11-05"
    Quand j'envoie une requête POST sur /booking avec cette réservation
    Alors le code de réponse est 400
    Et aucune réservation n'est créée

  Scénario: Type de donnée invalide
    Étant donné une réservation dont le champ "totalprice" vaut "cent"
    Quand j'envoie une requête POST sur /booking avec cette réservation
    Alors le code de réponse est 400
```

---

## US-04 — Consulter une réservation

**En tant qu'** application front,
**je veux** récupérer le détail d'une réservation à partir de son identifiant,
**afin d'** afficher le récapitulatif du séjour au client.

**Priorité** : Must · **Points** : 2

```gherkin
# language: fr
Fonctionnalité: Consultation d'une réservation

  Scénario: Réservation existante
    Étant donné une réservation existante
    Quand j'envoie une requête GET sur /booking/{bookingid} avec l'en-tête Accept "application/json"
    Alors le code de réponse est 200
    Et le corps respecte le schéma d'une réservation

  Scénario: Réservation inexistante
    Étant donné un identifiant qui ne correspond à aucune réservation
    Quand j'envoie une requête GET sur /booking/{identifiant}
    Alors le code de réponse est 404
```

---

## US-05 — Lister les réservations

**En tant que** partenaire,
**je veux** obtenir la liste des identifiants de réservation,
**afin de** synchroniser mon catalogue avec celui de l'hôtel.

**Priorité** : Should · **Points** : 1

```gherkin
# language: fr
Fonctionnalité: Liste des réservations

  Scénario: Liste complète
    Étant donné que j'ai créé une réservation
    Quand j'envoie une requête GET sur /booking
    Alors le code de réponse est 200
    Et le corps est un tableau d'objets contenant chacun un "bookingid" entier
    Et le tableau contient l'identifiant de la réservation créée
```

---

## US-06 — Rechercher des réservations par nom du client

**En tant que** partenaire,
**je veux** filtrer les réservations par prénom et/ou nom,
**afin de** retrouver rapidement la réservation d'un client.

**Priorité** : Should · **Points** : 3

```gherkin
# language: fr
Fonctionnalité: Recherche par nom

  Contexte:
    Étant donné une réservation existante au nom de "Prénom-unique Nom-unique"

  Scénario: Filtre sur le prénom et le nom
    Quand j'envoie une requête GET sur /booking?firstname=Prénom-unique&lastname=Nom-unique
    Alors le code de réponse est 200
    Et le résultat contient l'identifiant de la réservation

  Scénario: Filtre sur le prénom seul
    Quand j'envoie une requête GET sur /booking?firstname=Prénom-unique
    Alors le résultat contient l'identifiant de la réservation

  Scénario: Aucun résultat
    Quand j'envoie une requête GET sur /booking?firstname=PersonneInexistante
    Alors le code de réponse est 200
    Et le résultat est un tableau vide
```

---

## US-07 — Rechercher des réservations par dates de séjour

**En tant que** partenaire,
**je veux** filtrer les réservations selon leurs dates d'arrivée et de départ,
**afin de** connaître les séjours d'une période donnée.

**Priorité** : Could · **Points** : 3

```gherkin
# language: fr
Fonctionnalité: Recherche par dates

  Contexte:
    Étant donné une réservation existante du "2026-11-01" au "2026-11-05"

  Scénario: Date d'arrivée égale à la date du filtre
    Quand j'envoie une requête GET sur /booking?checkin=2026-11-01
    Alors le résultat contient l'identifiant de la réservation

  Scénario: Date d'arrivée postérieure à la date du filtre
    Quand j'envoie une requête GET sur /booking?checkin=2026-10-31
    Alors le résultat contient l'identifiant de la réservation

  Scénario: Date de départ supérieure ou égale à la date du filtre
    Quand j'envoie une requête GET sur /booking?checkout=2026-11-05
    Alors le résultat contient l'identifiant de la réservation

  Scénario: Format de date invalide
    Quand j'envoie une requête GET sur /booking?checkin=date-invalide
    Alors le code de réponse est 400
```

---

## US-08 — Modifier entièrement une réservation

**En tant qu'** administrateur,
**je veux** remplacer toutes les informations d'une réservation,
**afin de** prendre en compte une modification complète demandée par le client.

**Priorité** : Must · **Points** : 3

```gherkin
# language: fr
Fonctionnalité: Mise à jour complète d'une réservation

  Scénario: Mise à jour avec un jeton valide
    Étant donné une réservation existante
    Et un jeton d'authentification valide
    Quand j'envoie une requête PUT sur /booking/{bookingid} avec une réservation complète modifiée
    Alors le code de réponse est 200
    Et le corps contient les nouvelles valeurs
    Et une lecture ultérieure renvoie les nouvelles valeurs

  Scénario: Mise à jour avec Basic Auth
    Étant donné une réservation existante
    Quand j'envoie une requête PUT avec l'en-tête Authorization Basic des identifiants valides
    Alors le code de réponse est 200

  Scénario: Mise à jour d'une réservation inexistante
    Étant donné un jeton d'authentification valide
    Quand j'envoie une requête PUT sur /booking/{identifiant-inexistant}
    Alors le code de réponse est 404
```

---

## US-09 — Modifier partiellement une réservation

**En tant qu'** administrateur,
**je veux** modifier un ou plusieurs champs sans renvoyer toute la réservation,
**afin de** corriger rapidement une information, par exemple les demandes particulières.

**Priorité** : Should · **Points** : 3

```gherkin
# language: fr
Fonctionnalité: Mise à jour partielle d'une réservation

  Scénario: Modification d'un seul champ
    Étant donné une réservation existante dont "additionalneeds" vaut "Petit-déjeuner"
    Et un jeton d'authentification valide
    Quand j'envoie une requête PATCH sur /booking/{bookingid} avec {"additionalneeds": "Dîner"}
    Alors le code de réponse est 200
    Et "additionalneeds" vaut "Dîner"
    Et tous les autres champs sont inchangés
```

---

## US-10 — Supprimer une réservation

**En tant qu'** administrateur,
**je veux** supprimer une réservation annulée,
**afin qu'** elle n'apparaisse plus dans le système.

**Priorité** : Must · **Points** : 2

```gherkin
# language: fr
Fonctionnalité: Suppression d'une réservation

  Scénario: Suppression avec un jeton valide
    Étant donné une réservation existante
    Et un jeton d'authentification valide
    Quand j'envoie une requête DELETE sur /booking/{bookingid}
    Alors le code de réponse est 201
    Et une lecture ultérieure de la réservation renvoie 404

  Scénario: Suppression d'une réservation déjà supprimée
    Étant donné une réservation qui vient d'être supprimée
    Quand j'envoie à nouveau une requête DELETE sur /booking/{bookingid}
    Alors le code de réponse est 404
```

---

## US-11 — Protéger les opérations sensibles

**En tant qu'** administrateur,
**je veux** que seules les requêtes authentifiées puissent modifier ou supprimer une réservation,
**afin d'** empêcher toute altération des réservations par un tiers.

**Priorité** : Must · **Points** : 5

```gherkin
# language: fr
Fonctionnalité: Contrôle d'accès

  Plan du scénario: Opération protégée sans authentification valide
    Étant donné une réservation existante
    Quand j'envoie une requête <méthode> sur /booking/{bookingid} avec l'authentification <authentification>
    Alors le code de réponse est 403
    Et la réservation n'est pas modifiée

    Exemples:
      | méthode | authentification                  |
      | PUT     | aucune                            |
      | PUT     | jeton invalide                    |
      | PUT     | Basic Auth avec mauvais identifiants |
      | PATCH   | aucune                            |
      | PATCH   | jeton invalide                    |
      | DELETE  | aucune                            |
      | DELETE  | jeton invalide                    |
```

---

## US-12 — Recevoir des erreurs claires en cas de requête invalide

**En tant qu'** application front,
**je veux** recevoir un code d'erreur client explicite quand ma requête est invalide,
**afin d'** afficher un message utile à l'utilisateur au lieu d'un échec générique.

**Priorité** : Should · **Points** : 5

```gherkin
# language: fr
Fonctionnalité: Gestion des erreurs

  Scénario: Corps JSON mal formé
    Quand j'envoie une requête POST sur /booking avec un corps JSON mal formé
    Alors le code de réponse est 400

  Scénario: Une donnée invalide ne provoque jamais d'erreur serveur
    Quand j'envoie une requête POST sur /booking avec un champ obligatoire manquant ou de type incorrect
    Alors le code de réponse est 400
    Et le code de réponse n'est jamais 500
```
