# integration/kiteConnector.py

from kiteconnect import KiteConnect, KiteTicker
from datetime import datetime
from utils.logger import log

class KiteConnector:
    def __init__(self, api_key, api_secret, access_token=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.kite = KiteConnect(api_key=self.api_key)
        self.kws = None
        self.callback = None

        if access_token:
            self.kite.set_access_token(access_token)

    def get_login_url(self):
        return self.kite.login_url()

    def generate_session(self, request_token):
        session = self.kite.generate_session(request_token, api_secret=self.api_secret)
        self.access_token = session["access_token"]
        self.kite.set_access_token(self.access_token)
        return self.access_token

    def set_tick_callback(self, callback_fn):
        self.callback = callback_fn

    def start_websocket(self, instrument_tokens):
        if not self.access_token:
            raise Exception("Access token not set.")

        self.kws = KiteTicker(self.api_key, self.access_token)

        def on_ticks(ws, ticks):
            for tick in ticks:
                self.callback({
                    "symbol": tick["instrument_token"],
                    "price": tick.get("last_price"),
                    "timestamp": tick.get("timestamp", datetime.now())
                })

        def on_connect(ws, _):
            log("✅ Kite WebSocket connected.")
            ws.subscribe(instrument_tokens)

        def on_close(ws, code, reason):
            log(f"❌ WebSocket closed: {code} - {reason}")

        def on_error(ws, code, reason):
            log(f"⚠️ WebSocket error: {code} - {reason}")

        self.kws.on_ticks = on_ticks
        self.kws.on_connect = on_connect
        self.kws.on_close = on_close
        self.kws.on_error = on_error

        log("🔌 Connecting to Kite WebSocket...")
        self.kws.connect(threaded=True)
