// Test de charge LÉGÈRE de l'API Restful Booker (k6).
//
// L'API est publique et partagée : la charge est volontairement plafonnée à 5 utilisateurs
// virtuels (VU) pendant 30 secondes, avec une pause d'une seconde après chaque requête.
// Les résultats sont indicatifs (voir docs/qa/05_rapport_performance.md).
//
// Lancement : npm run test:perf   (ou : k6 run performance/charge_legere.js)

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import encoding from 'k6/encoding';

// Une seule source de configuration pour tout le projet : data/test_data.json
const donnees = JSON.parse(open('../data/test_data.json'));
const BASE_URL = __ENV.BOOKER_BASE_URL || donnees.configuration.base_url;
const IDENTIFIANTS = donnees.configuration.identifiants;
const BASIC_AUTH = `Basic ${encoding.b64encode(`${IDENTIFIANTS.username}:${IDENTIFIANTS.password}`)}`;
const PAUSE_S = 1;

export const options = {
  // Montée progressive, palier, descente : 30 s au total, 5 VU au maximum
  stages: [
    { duration: '5s', target: 5 },
    { duration: '20s', target: 5 },
    { duration: '5s', target: 0 },
  ],
  thresholds: {
    // Taux d'erreur HTTP < 1 %
    http_req_failed: ['rate<0.01'],
    // Toutes les vérifications fonctionnelles doivent réussir à plus de 99 %
    checks: ['rate>0.99'],
    // 95e percentile par endpoint : environ 3 fois le p95 mesuré le 05/10/2026 (2 mesures concordantes :
    // liste ≈ 182 ms, opérations unitaires ≈ 91 ms). La marge absorbe la variabilité d'une API
    // partagée tout en détectant une vraie dégradation. Justification : docs/qa/05_rapport_performance.md
    'http_req_duration{name:GET /booking}': ['p(95)<600'],
    'http_req_duration{name:GET /booking/{id}}': ['p(95)<300'],
    'http_req_duration{name:POST /booking}': ['p(95)<300'],
  },
  summaryTrendStats: ['min', 'avg', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
};

const EN_TETES_JSON = { 'Content-Type': 'application/json', Accept: 'application/json' };

export default function () {
  group('Lire la liste des réservations', () => {
    const reponse = http.get(`${BASE_URL}/booking`, { tags: { name: 'GET /booking' } });
    check(reponse, {
      'liste : code 200': (r) => r.status === 200,
      'liste : tableau JSON': (r) => Array.isArray(r.json()),
    });
  });
  sleep(PAUSE_S);

  let bookingId;
  group('Créer une réservation', () => {
    // Prénom unique par VU et par itération : nos données ne se mélangent pas aux autres
    const reservation = Object.assign({}, donnees.reservation_valide, {
      firstname: `K6${__VU}x${__ITER}x${Date.now()}`,
    });
    const reponse = http.post(`${BASE_URL}/booking`, JSON.stringify(reservation), {
      headers: EN_TETES_JSON,
      tags: { name: 'POST /booking' },
    });
    const ok = check(reponse, {
      'création : code 200': (r) => r.status === 200,
      'création : bookingid entier': (r) => Number.isInteger(r.json('bookingid')),
    });
    if (ok) {
      bookingId = reponse.json('bookingid');
    }
  });
  sleep(PAUSE_S);

  if (!bookingId) {
    return; // création en échec : déjà comptée dans les erreurs, rien à lire ni à supprimer
  }

  group('Lire une réservation', () => {
    const reponse = http.get(`${BASE_URL}/booking/${bookingId}`, {
      headers: { Accept: 'application/json' },
      tags: { name: 'GET /booking/{id}' },
    });
    check(reponse, {
      'lecture : code 200': (r) => r.status === 200,
      'lecture : prénom présent': (r) => typeof r.json('firstname') === 'string',
    });
  });
  sleep(PAUSE_S);

  // Nettoyage : chaque itération supprime la réservation qu'elle a créée (Basic Auth, insensible
  // aux purges de jetons). Ce n'est pas une opération mesurée du scénario : elle est taguée à part.
  const suppression = http.del(`${BASE_URL}/booking/${bookingId}`, null, {
    headers: { Authorization: BASIC_AUTH },
    tags: { name: 'DELETE /booking/{id} (nettoyage)' },
  });
  check(suppression, { 'nettoyage : code 201': (r) => r.status === 201 });
  sleep(PAUSE_S);
}
