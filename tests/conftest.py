"""Fixtures partagées : client API, authentification et données de test isolées."""
import copy
import uuid

import pytest

from tests.clients import BookerClient, charger_configuration, charger_donnees


# ---------------------------------------------------------------------- configuration
@pytest.fixture(scope="session")
def configuration() -> dict:
    return charger_configuration()


@pytest.fixture(scope="session")
def donnees() -> dict:
    return charger_donnees()


@pytest.fixture(scope="session")
def client(configuration) -> BookerClient:
    return BookerClient(configuration["base_url"], configuration["timeout_s"],
                        configuration["pause_entre_requetes_s"])


@pytest.fixture(scope="session")
def identifiants_admin(configuration) -> tuple[str, str]:
    """Identifiants de démonstration, au format attendu par Basic Auth."""
    return configuration["identifiants"]["username"], configuration["identifiants"]["password"]


@pytest.fixture(scope="session")
def token(client, configuration) -> str:
    """Jeton d'authentification, obtenu une seule fois pour toute la session de test."""
    reponse = client.create_token(configuration["identifiants"])
    assert reponse.status_code == 200, f"Impossible d'obtenir un jeton : {reponse.status_code} {reponse.text}"
    return reponse.json()["token"]


# ---------------------------------------------------------------------- données isolées
@pytest.fixture
def reservation_unique(donnees) -> dict:
    """Réservation valide dont le prénom et le nom sont uniques : elle ne peut pas être
    confondue avec les données des autres utilisateurs de l'API publique."""
    reservation = copy.deepcopy(donnees["reservation_valide"])
    suffixe = uuid.uuid4().hex[:10]
    reservation["firstname"] += suffixe
    reservation["lastname"] += suffixe
    return reservation


@pytest.fixture
def nettoyage(client, token):
    """Registre des réservations à supprimer après le test.

    Utilisé notamment par les cas négatifs : si l'API crée une réservation à tort, elle est
    enregistrée ici et supprimée au démontage, que le test réussisse ou non."""
    a_supprimer: list[int] = []

    def enregistrer(reponse):
        try:
            corps = reponse.json()
        except ValueError:
            return
        if isinstance(corps, dict) and "bookingid" in corps:
            a_supprimer.append(corps["bookingid"])

    yield enregistrer
    for booking_id in a_supprimer:
        client.delete_booking(booking_id, token=token)


@pytest.fixture
def reservation(client, reservation_unique, token):
    """Crée une réservation avant le test et la supprime après.

    Renvoie un dictionnaire {"id": ..., "donnees": ...}. La suppression finale tolère que le
    test ait déjà supprimé la réservation."""
    reponse = client.create_booking(reservation_unique)
    assert reponse.status_code == 200, f"Préparation impossible : {reponse.status_code} {reponse.text}"
    booking_id = reponse.json()["bookingid"]
    yield {"id": booking_id, "donnees": reservation_unique}
    client.delete_booking(booking_id, token=token)


# ---------------------------------------------------------------------- rapport HTML
def pytest_html_report_title(report):
    report.title = "Restful Booker — Rapport des tests d'API (pytest)"


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Description</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{getattr(report, 'description', '')}</td>")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    resultat = yield
    rapport = resultat.get_result()
    # La docstring du test (CT et comportement vérifié) apparaît dans le rapport HTML
    rapport.description = (item.function.__doc__ or "").strip().splitlines()[0] if item.function.__doc__ else ""
