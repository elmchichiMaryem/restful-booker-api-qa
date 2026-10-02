"""Tests de contrat : format des réponses (en-têtes et schémas JSON) de chaque endpoint JSON.

Les schémas (tests/schemas/) sont aussi utilisés par les tests fonctionnels ; ce module vérifie
en plus le type de contenu annoncé et le respect du format de date ISO 8601.
"""
import pytest

from tests.outils import valider_schema

pytestmark = [pytest.mark.regression, pytest.mark.contrat]


def _type_contenu(reponse) -> str:
    return reponse.headers.get("Content-Type", "").split(";")[0]


def test_contrat_creation_jeton(client, configuration):
    """CT-02 — POST /auth renvoie du JSON conforme au schéma « jeton »."""
    reponse = client.create_token(configuration["identifiants"])

    assert _type_contenu(reponse) == "application/json"
    valider_schema("jeton", reponse.json())


def test_contrat_creation_reservation(client, reservation_unique, nettoyage):
    """CT-06 — POST /booking renvoie du JSON conforme au schéma « reservation_creee » (dates ISO 8601)."""
    reponse = client.create_booking(reservation_unique)
    nettoyage(reponse)

    assert _type_contenu(reponse) == "application/json"
    valider_schema("reservation_creee", reponse.json())


def test_contrat_lecture_reservation(client, reservation):
    """CT-24 — GET /booking/{id} renvoie du JSON conforme au schéma « reservation »."""
    reponse = client.get_booking(reservation["id"])

    assert _type_contenu(reponse) == "application/json"
    valider_schema("reservation", reponse.json())


def test_contrat_liste_reservations(client):
    """CT-26 — GET /booking renvoie du JSON conforme au schéma « liste_identifiants »."""
    reponse = client.get_booking_ids()

    assert _type_contenu(reponse) == "application/json"
    valider_schema("liste_identifiants", reponse.json())


def test_schema_detecte_une_reponse_non_conforme():
    """Contrôle du dispositif : le schéma rejette bien une réservation corrompue (prix null, date 0NaN-aN-aN)."""
    corrompue = {"firstname": "A", "lastname": "B", "totalprice": None, "depositpaid": True,
                 "bookingdates": {"checkin": "0NaN-aN-aN", "checkout": "2026-11-05"}, "additionalneeds": "x"}

    with pytest.raises(AssertionError, match="totalprice") as erreur:
        valider_schema("reservation", corrompue)
    assert "checkin" in str(erreur.value)
