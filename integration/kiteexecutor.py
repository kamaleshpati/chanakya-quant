from utils.logger import log

class KiteExecutor:
    def __init__(self, kite):
        self.kite = kite  # Injected from KiteConnector

    def place_order(self, symbol, qty, side="BUY", order_type="MARKET", product="MIS"):
        try:
            order_id = self.kite.place_order(
                variety="regular",
                exchange="NSE",
                tradingsymbol=symbol,
                transaction_type=side,
                quantity=qty,
                order_type=order_type,
                product=product
            )
            log(f"✅ Order placed: {side} {qty} {symbol} | ID: {order_id}")
            return order_id
        except Exception as e:
            log(f"❌ Failed to place order: {e}")
            return None

    def get_positions(self):
        return self.kite.positions()

    def get_holdings(self):
        return self.kite.holdings()
