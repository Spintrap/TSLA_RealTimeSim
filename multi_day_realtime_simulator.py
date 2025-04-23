import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# === Config ===
data_dir = "tsla_data_1min"
filename = "TSLA_2025-04-08.csv"  # File must exist in tsla_data_1min/

# === Load Data ===
file_path = os.path.join(data_dir, filename)
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

try:
    df = pd.read_csv(file_path, parse_dates=['date'])
except Exception as e:
    print(f"Failed to read CSV: {e}")
    exit()

print("\n=== File Preview ===")
print(df.head())
print("\nColumns:", df.columns.tolist())
print(f"Total rows: {len(df)}\n")

if 'close' not in df.columns or 'date' not in df.columns or len(df) < 25:
    print("CSV file missing required columns or too few rows.")
    exit()

# === Set datetime index ===
df.set_index('date', inplace=True)

# === Strategy Parameters ===
entry_buffer = 0.10
reward_ratio = 1.2
risk_per_trade = 100

# === Tracking ===
trades = []
in_trade = False
entry_price = 0
stop_loss = 0
take_profit = 0
position_size = 0
entry_index = None
trade_entry_time = None

# === Strategy Logic ===
for i in range(20, len(df)):
    bar = df.iloc[i]
    timestamp = df.index[i]
    close = bar['close']

    if not in_trade and i % 6 == 0:
        print(f"FORCED ENTRY at {timestamp} | Close: {close}")
        entry_price = close
        stop_loss = entry_price - 1.0
        take_profit = entry_price + reward_ratio * (entry_price - stop_loss)
        position_size = round(risk_per_trade / (entry_price - stop_loss))
        entry_index = i
        in_trade = True
        trade_entry_time = timestamp

    elif in_trade:
        if i - entry_index >= 5:
            pnl = (close - entry_price) * position_size
            trades.append({
                'entry_time': trade_entry_time,
                'exit_time': timestamp,
                'entry_price': entry_price,
                'exit_price': close,
                'net_pnl': round(pnl, 2)
            })
            in_trade = False

# === Output ===
trades_df = pd.DataFrame(trades)
if trades_df.empty:
    print("No trades executed.")
else:
    print(trades_df)
    trades_df['cumulative_pnl'] = trades_df['net_pnl'].cumsum()

    # Plot equity curve
    plt.figure(figsize=(10, 5))
    plt.plot(trades_df['exit_time'], trades_df['cumulative_pnl'], label='Equity Curve')
    plt.axhline(0, linestyle='--', color='gray')
    plt.title("TSLA Strategy Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Cumulative PnL ($)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
