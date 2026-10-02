"""Chargement de la configuration et des jeux de données de test.

Toutes les valeurs proviennent de data/test_data.json. L'URL et les identifiants peuvent être
surchargés par variables d'environnement (utile en CI ou pour cibler un autre environnement) :
BOOKER_BASE_URL, BOOKER_USERNAME, BOOKER_PASSWORD.
"""
import json
import os
from functools import lru_cache
from pathlib import Path

FICHIER_DONNEES = Path(__file__).resolve().parents[2] / "data" / "test_data.json"


@lru_cache(maxsize=1)
def charger_donnees() -> dict:
    """Renvoie le contenu complet de data/test_data.json (lu une seule fois)."""
    with FICHIER_DONNEES.open(encoding="utf-8") as fichier:
        return json.load(fichier)


def charger_configuration() -> dict:
    """Renvoie la section « configuration », avec les surcharges éventuelles."""
    configuration = json.loads(json.dumps(charger_donnees()["configuration"]))  # copie profonde
    configuration["base_url"] = os.getenv("BOOKER_BASE_URL", configuration["base_url"]).rstrip("/")
    identifiants = configuration["identifiants"]
    identifiants["username"] = os.getenv("BOOKER_USERNAME", identifiants["username"])
    identifiants["password"] = os.getenv("BOOKER_PASSWORD", identifiants["password"])
    return configuration
