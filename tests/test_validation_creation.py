"""US-03 et US-12 : rejet des données invalides à la création d'une réservation (RG-01 à RG-07, RG-18).

Les cas sont décrits dans data/test_data.json ; ceux qui portent une référence BUG-xx sont
marqués xfail strict (anomalie connue).
"""
import copy

import pytest

from tests.clients import charger_donnees
from tests.outils import parametre

pytestmark = pytest.mark.regression

DONNEES = charger_donnees()
CHAMPS_OBLIGATOIRES = [parametre(cas, cas["champ"], id_cas=f"sans-{cas['champ']}")
                       for cas in DONNEES["champs_obligatoires"]]
VALEURS_INVALIDES = [parametre(cas, cas["surcharge"], id_cas=cas["id"])
                     for cas in DONNEES["valeurs_invalides"]]


@pytest.mark.parametrize("champ", CHAMPS_OBLIGATOIRES)
def test_creation_refusee_si_champ_obligatoire_absent(client, reservation_unique, nettoyage, champ):
    """CT-08 à CT-13 — Une réservation sans champ obligatoire est refusée avec 400."""
    del reservation_unique[champ]

    reponse = client.create_booking(reservation_unique)
    nettoyage(reponse)

    assert reponse.status_code == 400


@pytest.mark.parametrize("surcharge", VALEURS_INVALIDES)
def test_creation_refusee_si_valeur_invalide(client, reservation_unique, nettoyage, surcharge):
    """CT-14 à CT-22 — Une valeur de type, de format ou de cohérence invalide est refusée avec 400."""
    reservation = {**reservation_unique, **copy.deepcopy(surcharge)}

    reponse = client.create_booking(reservation)
    nettoyage(reponse)

    assert reponse.status_code == 400


def test_creation_refusee_si_json_mal_forme(client, donnees, nettoyage):
    """CT-23 — Un corps JSON mal formé est refusé avec 400."""
    reponse = client.create_booking(corps_brut=donnees["json_mal_forme"])
    nettoyage(reponse)

    assert reponse.status_code == 400

