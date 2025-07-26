import numpy as np
import pandas as pd

def backtest(df, initial_capital=1000000, sl_pct=0.015, tp_pct=0.025):
    df = df.copy()
    df['Position'] = 0
    df['Equity'] = initial_capital
    trades = []
    in_trade = False

    for i in range(1, len(df)):
        price = df['Close'].iloc[i]
        signal = df['Signal'].iloc[i]

        if not in_trade:
            if signal == 1:
                entry_price = price
                stop_loss = entry_price * (1 - sl_pct)
                take_profit = entry_price * (1 + tp_pct)
                entry_time = df.index[i]
                side = 'long'
                in_trade = True
            elif signal == -1:
                entry_price = price
                stop_loss = entry_price * (1 + sl_pct)
                take_profit = entry_price * (1 - tp_pct)
                entry_time = df.index[i]
                side = 'short'
                in_trade = True
        else:
            if side == 'long':
                if price <= stop_loss:
                    exit_reason = 'SL'
                elif price >= take_profit:
                    exit_reason = 'TP'
                elif signal == -1:
                    exit_reason = 'REV'
                else:
                    continue
                pnl = price - entry_price
            elif side == 'short':
                if price >= stop_loss:
                    exit_reason = 'SL'
                elif price <= take_profit:
                    exit_reason = 'TP'
                elif signal == 1:
                    exit_reason = 'REV'
                else:
                    continue
                pnl = entry_price - price

            trades.append({
                'Entry Time': entry_time,
                'Exit Time': df.index[i],
                'Entry Price': entry_price,
                'Exit Price': price,
                'Side': side,
                'PnL': pnl,
                'Exit Reason': exit_reason
            })
            in_trade = False

    # Create trade DataFrame
    trade_df = pd.DataFrame(trades)
    equity = [initial_capital]

    for pnl in trade_df['PnL']:
        equity.append(equity[-1] + pnl)
    trade_df['Equity'] = equity[1:]

    # Metrics
    total_return = (equity[-1] / initial_capital) - 1
    returns = trade_df['PnL'] / initial_capital
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(len(trade_df)) if len(trade_df) > 1 else 0
    max_dd = max([max(equity[:i]) - equity[i] for i in range(1, len(equity))])

    print(f"Total Return: {total_return*100:.2f}%")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: ₹{max_dd:.2f}")
    print(f"Total Trades: {len(trade_df)}")
    print(trade_df.tail())

    return trade_df