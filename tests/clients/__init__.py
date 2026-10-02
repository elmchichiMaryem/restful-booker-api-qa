"""Client réutilisable de l'API Restful Booker et chargement de la configuration."""
from tests.clients.booker_client import BookerClient
from tests.clients.config import charger_configuration, charger_donnees

__all__ = ["BookerClient", "charger_configuration", "charger_donnees"]
