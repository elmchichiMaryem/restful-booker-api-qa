"""Client HTTP de l'API Restful Booker : une méthode par endpoint.

Les méthodes renvoient la réponse brute (requests.Response) : c'est aux tests de vérifier le
code HTTP et le corps, y compris dans les cas d'erreur.

Authentification des opérations protégées (PUT, PATCH, DELETE) : passer soit `token`
(envoyé dans l'en-tête Cookie), soit `basic` (tuple identifiant, mot de passe), soit rien.
"""
import time

import requests


class BookerClient:
    def __init__(self, base_url: str, timeout_s: float = 30, pause_s: float = 0.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.pause_s = pause_s
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------ outils internes
    def _requete(self, methode, chemin, token=None, basic=None, **kwargs) -> requests.Response:
        # Pause systématique : l'API est publique et partagée, on reste en charge légère
        if self.pause_s:
            time.sleep(self.pause_s)
        en_tetes = kwargs.pop("headers", {})
        if token is not None:
            en_tetes["Cookie"] = f"token={token}"
        return self.session.request(
            methode, f"{self.base_url}{chemin}", headers=en_tetes, auth=basic,
            timeout=self.timeout_s, **kwargs,
        )

    # ------------------------------------------------------------------ endpoints
    def ping(self) -> requests.Response:
        """GET /ping — contrôle de santé."""
        return self._requete("GET", "/ping")

    def create_token(self, corps: dict) -> requests.Response:
        """POST /auth — corps attendu : {"username": ..., "password": ...}."""
        return self._requete("POST", "/auth", json=corps)

    def get_booking_ids(self, **filtres) -> requests.Response:
        """GET /booking — filtres optionnels : firstname, lastname, checkin, checkout."""
        return self._requete("GET", "/booking", params=filtres)

    def get_booking(self, booking_id) -> requests.Response:
        """GET /booking/{id}."""
        return self._requete("GET", f"/booking/{booking_id}")

    def create_booking(self, reservation: dict | None = None, corps_brut: str | None = None) -> requests.Response:
        """POST /booking — `corps_brut` permet d'envoyer un JSON volontairement mal formé."""
        if corps_brut is not None:
            return self._requete("POST", "/booking", data=corps_brut,
                                 headers={"Content-Type": "application/json"})
        return self._requete("POST", "/booking", json=reservation)

    def update_booking(self, booking_id, reservation: dict, token=None, basic=None) -> requests.Response:
        """PUT /booking/{id} — remplacement complet (authentification requise)."""
        return self._requete("PUT", f"/booking/{booking_id}", token=token, basic=basic, json=reservation)

    def partial_update_booking(self, booking_id, champs: dict, token=None, basic=None) -> requests.Response:
        """PATCH /booking/{id} — modification partielle (authentification requise)."""
        return self._requete("PATCH", f"/booking/{booking_id}", token=token, basic=basic, json=champs)

    def delete_booking(self, booking_id, token=None, basic=None) -> requests.Response:
        """DELETE /booking/{id} — suppression (authentification requise)."""
        return self._requete("DELETE", f"/booking/{booking_id}", token=token, basic=basic)
