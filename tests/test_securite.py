"""US-11 : les opérations protégées refusent tout accès non authentifié (RG-09).

Matrice complète méthode × type d'authentification invalide. Après chaque tentative, une
relecture vérifie que la réservation n'a été ni modifiée ni supprimée.
"""
import pytest

pytestmark = [pytest.mark.regression, pytest.mark.securite]

AUTHENTIFICATIONS_INVALIDES = ["sans-auth", "jeton-invalide", "basic-invalide"]
OPERATIONS = ["PUT", "PATCH", "DELETE"]
# Correspondance avec les cas de test manuels (les autres combinaisons complètent la matrice)
CAS_DE_TEST = {
    ("PUT", "sans-auth"): "CT-41", ("PUT", "jeton-invalide"): "CT-42", ("PUT", "basic-invalide"): "CT-43",
    ("PATCH", "sans-auth"): "CT-44", ("PATCH", "jeton-invalide"): "CT-45",
    ("DELETE", "sans-auth"): "CT-46", ("DELETE", "jeton-invalide"): "CT-47",
}
MATRICE = [
    pytest.param(operation, auth, id=f"{CAS_DE_TEST.get((operation, auth), 'complement')}-{operation.lower()}-{auth}")
    for operation in OPERATIONS for auth in AUTHENTIFICATIONS_INVALIDES
]


@pytest.fixture
def authentification_invalide(donnees, identifiants_admin):
    """Arguments du client pour chaque type d'authentification invalide."""
    return {
        "sans-auth": {},
        "jeton-invalide": {"token": donnees["jeton_invalide"]},
        "basic-invalide": {"basic": (identifiants_admin[0], donnees["mot_de_passe_invalide"])},
    }


@pytest.mark.parametrize("operation, auth", MATRICE)
def test_operation_protegee_refusee_sans_authentification_valide(
        client, reservation, donnees, authentification_invalide, operation, auth):
    """CT-41 à CT-47 — Sans authentification valide, PUT/PATCH/DELETE renvoient 403 et la réservation est inchangée."""
    booking_id, arguments = reservation["id"], authentification_invalide[auth]
    tentative = {**reservation["donnees"], "firstname": "Pirate"}
    appels = {
        "PUT": lambda: client.update_booking(booking_id, tentative, **arguments),
        "PATCH": lambda: client.partial_update_booking(booking_id, {"firstname": "Pirate"}, **arguments),
        "DELETE": lambda: client.delete_booking(booking_id, **arguments),
    }

    reponse = appels[operation]()

    assert reponse.status_code == 403
    relecture = client.get_booking(booking_id)
    assert relecture.status_code == 200
    assert relecture.json() == reservation["donnees"]
