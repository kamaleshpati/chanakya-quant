# main.py

import signal
import time
import atexit
from datetime import datetime

from integration.kiteconnector import KiteConnector
from integration.kiteconnector import KiteIntegration
from config.settings import Settings
from utils.logger import log

running = True

def signal_handler(sig, frame):
    global running
    log("🛑 Ctrl+C detected. Exiting...")
    running = False

def on_exit():
    log("🧹 Cleanup done. ChanakyaQuant shutting down.")

def main():
    global running

    signal.signal(signal.SIGINT, signal_handler)
    atexit.register(on_exit)

    try:
        config = Settings.load()

        kite_connector = KiteConnector(
            api_key=config.ZERODHA_API_KEY,
            api_secret=config.ZERODHA_API_SECRET,
            access_token=config.ZERODHA_ACCESS_TOKEN
        )

        integration = KiteIntegration(kite_connector, config)

        # Subscribe to tick stream
        kite_connector.set_tick_callback(integration.handle_tick)
        kite_connector.start_websocket([256265, 260105])  # NIFTY, BANKNIFTY

        while running:
            integration.finalize_bar(datetime.now())
            time.sleep(2)

    except Exception as e:
        log(f"❌ Error in main: {e}")

if __name__ == "__main__":
    main()
