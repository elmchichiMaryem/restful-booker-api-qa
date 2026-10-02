"""US-06 et US-07 : recherche de réservations par nom et par dates (RG-16, RG-17).

Chaque recherche est combinée au prénom unique de la réservation créée par la fixture : le
résultat ne dépend donc d'aucune donnée tierce de l'API publique.
"""
import pytest

from tests.clients import charger_donnees
from tests.outils import anomalie_connue, identifiants, parametre, valider_schema

pytestmark = pytest.mark.regression

DONNEES = charger_donnees()
FILTRES_DATES = [parametre(cas, cas["parametres"], cas["doit_contenir"], id_cas=cas["id"])
                 for cas in DONNEES["filtres_dates"]["cas"]]


@pytest.mark.smoke
@pytest.mark.contrat
def test_filtrer_par_prenom_et_nom(client, reservation):
    """CT-27 — Le filtre prénom + nom renvoie la réservation correspondante."""
    reponse = client.get_booking_ids(firstname=reservation["donnees"]["firstname"],
                                     lastname=reservation["donnees"]["lastname"])

    assert reponse.status_code == 200
    valider_schema("liste_identifiants", reponse.json())
    assert identifiants(reponse) == [reservation["id"]]


def test_filtrer_par_prenom(client, reservation):
    """CT-28 — Le filtre prénom seul renvoie la réservation correspondante."""
    reponse = client.get_booking_ids(firstname=reservation["donnees"]["firstname"])

    assert reponse.status_code == 200
    assert reservation["id"] in identifiants(reponse)


def test_filtrer_par_prenom_inexistant(client, reservation_unique):
    """CT-29 — Un prénom sans réservation renvoie 200 et une liste vide."""
    reponse = client.get_booking_ids(firstname=f"Inexistant{reservation_unique['firstname']}")

    assert reponse.status_code == 200
    assert reponse.json() == []


@pytest.mark.parametrize("parametres, doit_contenir", FILTRES_DATES)
def test_filtrer_par_dates(client, reservation, parametres, doit_contenir):
    """CT-30 à CT-32, CT-51 à CT-53 — Les filtres checkin/checkout renvoient les dates ≥ à la date fournie."""
    reponse = client.get_booking_ids(firstname=reservation["donnees"]["firstname"], **parametres)

    assert reponse.status_code == 200
    assert (reservation["id"] in identifiants(reponse)) is doit_contenir


@anomalie_connue("BUG-11")
def test_filtrer_avec_date_invalide(client, donnees):
    """CT-33 — Un filtre de date au format invalide renvoie 400."""
    reponse = client.get_booking_ids(**donnees["filtre_date_invalide"])

    assert reponse.status_code == 400
