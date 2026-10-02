"""US-03 à US-05, US-08 à US-10 : cycle de vie d'une réservation (créer, lire, modifier, supprimer)."""
import pytest

from tests.clients import charger_donnees
from tests.outils import anomalie_connue, identifiants, valider_schema, verifier_temps_reponse

pytestmark = pytest.mark.regression

DONNEES = charger_donnees()
# Les deux moyens d'authentification documentés, utilisés pour paramétrer les opérations protégées
MODES_AUTH = ["jeton", "basic"]


@pytest.fixture
def authentification(request, token, identifiants_admin) -> dict:
    """Arguments d'authentification du client pour le mode demandé (jeton en cookie ou Basic Auth)."""
    return {"token": token} if request.param == "jeton" else {"basic": identifiants_admin}


# ---------------------------------------------------------------------- création et lecture
@pytest.mark.smoke
@pytest.mark.contrat
def test_creer_reservation(client, reservation_unique, nettoyage, configuration):
    """CT-06 — POST /booking avec des données valides renvoie 200, un identifiant et les données envoyées."""
    reponse = client.create_booking(reservation_unique)
    nettoyage(reponse)

    assert reponse.status_code == 200
    valider_schema("reservation_creee", reponse.json())
    assert reponse.json()["booking"] == reservation_unique
    verifier_temps_reponse(reponse, configuration["temps_reponse_max_ms"])


@pytest.mark.smoke
@pytest.mark.contrat
def test_lire_reservation(client, reservation, configuration):
    """CT-07, CT-24 — GET /booking/{id} renvoie 200 et les données enregistrées à la création."""
    reponse = client.get_booking(reservation["id"])

    assert reponse.status_code == 200
    valider_schema("reservation", reponse.json())
    assert reponse.json() == reservation["donnees"]
    verifier_temps_reponse(reponse, configuration["temps_reponse_max_ms"])


@pytest.mark.contrat
def test_lister_reservations(client, reservation):
    """CT-26 — GET /booking renvoie la liste des identifiants, qui contient la réservation créée."""
    reponse = client.get_booking_ids()

    assert reponse.status_code == 200
    valider_schema("liste_identifiants", reponse.json())
    assert reservation["id"] in identifiants(reponse)


def test_lire_reservation_inexistante(client, donnees):
    """CT-25 — GET /booking/{id} sur un identifiant inexistant renvoie 404."""
    reponse = client.get_booking(donnees["identifiant_inexistant"])

    assert reponse.status_code == 404


# ---------------------------------------------------------------------- modification
@pytest.mark.smoke
@pytest.mark.parametrize("authentification", MODES_AUTH, indirect=True)
def test_modifier_entierement_reservation(client, reservation, authentification, donnees):
    """CT-34, CT-35 — PUT /booking/{id} authentifié remplace la réservation ; la modification est persistée."""
    nouvelle = {**reservation["donnees"], **donnees["reservation_modifiee"]}

    reponse = client.update_booking(reservation["id"], nouvelle, **authentification)

    assert reponse.status_code == 200
    valider_schema("reservation", reponse.json())
    assert reponse.json() == nouvelle
    assert client.get_booking(reservation["id"]).json() == nouvelle


@pytest.mark.parametrize("authentification", MODES_AUTH, indirect=True)
def test_modifier_partiellement_reservation(client, reservation, authentification, donnees):
    """CT-38 — PATCH /booking/{id} ne modifie que les champs envoyés."""
    champs = donnees["modification_partielle"]

    reponse = client.partial_update_booking(reservation["id"], champs, **authentification)

    assert reponse.status_code == 200
    valider_schema("reservation", reponse.json())
    assert reponse.json() == {**reservation["donnees"], **champs}


def test_modifier_avec_corps_incomplet_refuse(client, reservation, token):
    """CT-37 — PUT /booking/{id} sans champ obligatoire renvoie 400 et ne modifie pas la réservation."""
    incomplete = {cle: valeur for cle, valeur in reservation["donnees"].items() if cle != "lastname"}

    reponse = client.update_booking(reservation["id"], incomplete, token=token)

    assert reponse.status_code == 400
    assert client.get_booking(reservation["id"]).json() == reservation["donnees"]


@anomalie_connue("BUG-05")
def test_modifier_partiellement_dates_incoherentes_refuse(client, reservation, token):
    """CT-40 — PATCH avec une date de départ antérieure à l'arrivée renvoie 400."""
    dates = {"bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-01"}}

    reponse = client.partial_update_booking(reservation["id"], dates, token=token)

    assert reponse.status_code == 400


# ---------------------------------------------------------------------- suppression
@pytest.mark.smoke
@pytest.mark.parametrize("authentification", MODES_AUTH, indirect=True)
def test_supprimer_reservation(client, reservation, authentification):
    """CT-48, CT-50 — DELETE /booking/{id} authentifié renvoie 201, puis la réservation est introuvable (404)."""
    reponse = client.delete_booking(reservation["id"], **authentification)

    assert reponse.status_code == 201
    assert client.get_booking(reservation["id"]).status_code == 404


# ---------------------------------------------------------------------- ressource inexistante
@anomalie_connue("BUG-14")
@pytest.mark.parametrize("operation", ["PUT", "PATCH", "DELETE"], ids=["CT-36-put", "CT-39-patch", "delete-identifiant-inexistant"])
def test_operation_sur_reservation_inexistante(client, token, donnees, reservation_unique, operation):
    """CT-36, CT-39 — Une opération authentifiée sur une réservation inexistante renvoie 404."""
    booking_id = donnees["identifiant_inexistant"]
    appels = {
        "PUT": lambda: client.update_booking(booking_id, reservation_unique, token=token),
        "PATCH": lambda: client.partial_update_booking(booking_id, donnees["modification_partielle"], token=token),
        "DELETE": lambda: client.delete_booking(booking_id, token=token),
    }

    reponse = appels[operation]()

    assert reponse.status_code == 404


@anomalie_connue("BUG-14")
def test_supprimer_reservation_deja_supprimee(client, reservation, token):
    """CT-49 — Un second DELETE sur une réservation déjà supprimée renvoie 404."""
    assert client.delete_booking(reservation["id"], token=token).status_code == 201

    reponse = client.delete_booking(reservation["id"], token=token)

    assert reponse.status_code == 404
