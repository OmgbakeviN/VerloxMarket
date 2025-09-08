import threading
import time
import random
import math
from collections import deque
from datetime import datetime, timezone

# --- Paramètres globaux ---
UPDATE_INTERVAL_SEC = 1.0      # fréquence des ticks
WINDOW_DEFAULT = 120           # taille de la fenêtre glissante
BASE_PRICE = 100.0             # prix initial par défaut

# mapping volatilité -> sigma (écart-type par tick)
SIGMA_BY_VOL = {
    "LOW":  0.0008,
    "MID":  0.0015,
    "HIGH": 0.0030,
}

class _PriceEngine:
    """
    Singleton en mémoire: maintient, pour chaque company_id:
      - prix courant
      - fenêtre glissante de ticks (deque maxlen)
      - paramètres (sigma) selon 'volatility'
    Un thread met à jour les prix chaque seconde (marche aléatoire multiplicative).
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        # company_id -> dict(state)
        self._state = {}
        self._thread = None

    def start(self):
        """
        Démarre le thread si pas déjà démarré.
        """
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def register_company(self, company_id: int, volatility: str, base_price: float = BASE_PRICE):
        """
        Enregistre une company si absente. Idempotent.
        """
        sigma = SIGMA_BY_VOL.get(volatility, SIGMA_BY_VOL["MID"])
        with self._lock:
            if company_id not in self._state:
                dq = deque(maxlen=WINDOW_DEFAULT)
                ts = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                dq.append({"t": ts, "price": base_price})
                self._state[company_id] = {
                    "price": base_price,
                    "sigma": sigma,
                    "volatility": volatility,
                    "ticks": dq,
                }

    def get_ticks(self, company_id: int, window: int = WINDOW_DEFAULT):
        """
        Retourne les derniers 'window' points sous forme de liste [{t, price}, ...]
        """
        with self._lock:
            st = self._state.get(company_id)
            if not st:
                return []
            # renvoie une slice de la deque
            data = list(st["ticks"])
        if window and window > 0:
            data = data[-window:]
        return data

    def _loop(self):
        """
        Boucle d’update temps réel (1s).
        """
        while True:
            time.sleep(UPDATE_INTERVAL_SEC)
            now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
            with self._lock:
                # met à jour toutes les companies enregistrées
                for cid, st in self._state.items():
                    p = st["price"]
                    sigma = st["sigma"]
                    # bruit gaussien ~ N(0, sigma)
                    shock = random.gauss(0.0, sigma)
                    # marche multiplicative (GBM simplifiée sans drift)
                    new_price = max(0.000001, p * (1.0 + shock))
                    st["price"] = new_price
                    st["ticks"].append({"t": now_ms, "price": round(new_price, 6)})

# instance globale (singleton)
_engine = _PriceEngine()

def start_engine():
    _engine.start()

def ensure_company_registered(company_id: int, volatility: str, base_price: float = BASE_PRICE):
    _engine.register_company(company_id, volatility, base_price)

def get_ticks(company_id: int, window: int = WINDOW_DEFAULT):
    return _engine.get_ticks(company_id, window)
