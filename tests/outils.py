"""Outils partagés par les tests : validation de schéma et marquage des anomalies connues."""
import json
from functools import lru_cache
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

DOSSIER_SCHEMAS = Path(__file__).parent / "schemas"

# Catalogue des anomalies documentées dans docs/qa/03_rapports_anomalies.md
ANOMALIES = {
    "BUG-01": "POST /auth : un échec d'authentification renvoie 200 au lieu de 401/400",
    "BUG-02": "POST /booking : champ obligatoire manquant ou nom de type incorrect → 500 au lieu de 400",
    "BUG-03": "POST /booking : prix non numérique accepté et enregistré à null",
    "BUG-04": "POST /booking : depositpaid non booléen converti (\"false\" devient true)",
    "BUG-05": "POST/PATCH /booking : date de départ antérieure ou égale à l'arrivée acceptée",
    "BUG-06": "POST /booking : date invalide enregistrée sous la forme 0NaN-aN-aN",
    "BUG-07": "POST /booking : date inexistante (30 février) convertie silencieusement",
    "BUG-08": "POST /booking : prix négatif accepté",
    "BUG-09": "POST /booking : prénom vide accepté",
    "BUG-10": "POST /booking : additionalneeds, documenté obligatoire, est facultatif",
    "BUG-11": "GET /booking : filtre de date invalide → 500 au lieu de 400",
    "BUG-12": "GET /booking : le filtre checkin exclut la date égale (> au lieu de ≥)",
    "BUG-13": "GET /booking : le filtre checkout est inversé (≤ au lieu de ≥)",
    "BUG-14": "PUT/PATCH/DELETE sur une réservation inexistante → 405 au lieu de 404",
}


def anomalie_connue(bug: str):
    """Marqueur xfail strict : le test vérifie le comportement attendu et doit échouer tant que
    l'anomalie existe. S'il passe (XPASS), la suite échoue : l'anomalie semble corrigée et le
    marquage doit être retiré."""
    return pytest.mark.xfail(strict=True, reason=f"{bug} — {ANOMALIES[bug]}")


def parametre(cas: dict, *valeurs, id_cas: str):
    """Construit un pytest.param, marqué xfail si le cas porte une référence d'anomalie."""
    marques = [anomalie_connue(cas["bug"])] if cas.get("bug") else []
    return pytest.param(*valeurs, id=f"{cas['ct']}-{id_cas}", marks=marques)


@lru_cache(maxsize=1)
def _registre() -> Registry:
    ressources = []
    for fichier in DOSSIER_SCHEMAS.glob("*.json"):
        contenu = json.loads(fichier.read_text(encoding="utf-8"))
        ressources.append((contenu["$id"], Resource.from_contents(contenu)))
    return Registry().with_resources(ressources)


def valider_schema(nom: str, instance) -> None:
    """Valide `instance` contre tests/schemas/<nom>.json ; lève AssertionError avec le détail."""
    schema = _registre().contents(f"{nom}.json")
    validateur = Draft202012Validator(schema, registry=_registre(), format_checker=FormatChecker())
    erreurs = sorted(validateur.iter_errors(instance), key=lambda e: list(e.path))
    assert not erreurs, f"Réponse non conforme au schéma {nom} : " + " ; ".join(
        f"{'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in erreurs)


def identifiants(reponse) -> list[int]:
    """Liste des bookingid d'une réponse GET /booking."""
    return [element["bookingid"] for element in reponse.json()]


def verifier_temps_reponse(reponse, maximum_ms: int) -> None:
    """Vérifie que la réponse est arrivée sous le seuil défini dans la configuration."""
    duree_ms = reponse.elapsed.total_seconds() * 1000
    assert duree_ms < maximum_ms, f"Temps de réponse {duree_ms:.0f} ms ≥ seuil {maximum_ms} ms"
