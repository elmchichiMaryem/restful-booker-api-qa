"""US-01 et US-02 : disponibilité de l'API et obtention d'un jeton d'authentification."""
import pytest

from tests.clients import charger_donnees
from tests.outils import parametre, valider_schema, verifier_temps_reponse

pytestmark = pytest.mark.regression

DONNEES = charger_donnees()
AUTH_INVALIDES = [parametre(cas, cas["corps"], cas["code_attendu"], id_cas=cas["id"])
                  for cas in DONNEES["authentification_invalide"]]


@pytest.mark.smoke
def test_ping_api_disponible(client, configuration):
    """CT-01 — GET /ping renvoie 201 « Created »."""
    reponse = client.ping()

    assert reponse.status_code == 201
    assert reponse.text == "Created"
    verifier_temps_reponse(reponse, configuration["temps_reponse_max_ms"])


@pytest.mark.smoke
@pytest.mark.contrat
def test_jeton_delivre_avec_identifiants_valides(client, configuration):
    """CT-02 — POST /auth avec les identifiants valides renvoie 200 et un jeton non vide."""
    reponse = client.create_token(configuration["identifiants"])

    assert reponse.status_code == 200
    valider_schema("jeton", reponse.json())
    verifier_temps_reponse(reponse, configuration["temps_reponse_max_ms"])


@pytest.mark.securite
@pytest.mark.parametrize("corps", [cas["corps"] for cas in DONNEES["authentification_invalide"]],
                         ids=[f"{cas['ct']}-{cas['id']}" for cas in DONNEES["authentification_invalide"]])
def test_aucun_jeton_sans_identifiants_valides(client, corps):
    """CT-03 à CT-05 — Aucun jeton n'est délivré sans identifiants valides."""
    reponse = client.create_token(corps)

    assert "token" not in reponse.json()


@pytest.mark.securite
@pytest.mark.parametrize("corps, code_attendu", AUTH_INVALIDES)
def test_code_http_echec_authentification(client, corps, code_attendu):
    """CT-03 à CT-05 — Un échec d'authentification renvoie 401 (mauvais identifiants) ou 400 (corps incomplet)."""
    reponse = client.create_token(corps)

    assert reponse.status_code == code_attendu
