import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# We are importing the functions you ALREADY built in your main Project 3 file!
# This keeps your code clean and prevents you from copying/pasting massive blocks of math.
from project_3_main import (
    get_cleaned_data, 
    align_assets, 
    run_kalman_filter, 
    calculate_dynamic_spread, 
    calculate_dynamic_zscore
)

def calculate_backtest_pnl(y_clean, x_clean, dynamic_hr, z_score):
    """
    THE ACCOUNTANT:
    Institutional-grade vectorized execution. No slow for-loops. We use 
    pandas broadcasting to process the entire 5-year timeline in milliseconds.
    """
    print("\n-> Accountant: Opening the ledgers (Vectorized Mode)...")
    
    # Calculate daily percentage returns for both assets
    y_returns = y_clean.pct_change().fillna(0)
    x_returns = x_clean.pct_change().fillna(0)
    
    # --- THE VECTORIZED TRADING LOGIC ---
    # 1. Create an empty ledger filled with NaNs (Not A Number)
    positions = pd.Series(np.nan, index=z_score.index)
    
    # 2. The Entry Signals (Boolean Masking)
    # Pandas instantly stamps a 1 or -1 on any day that crosses the thresholds.
    positions[z_score <= -1.90] = 1   # Spread is too low -> LONG
    positions[z_score >= 1.90] = -1   # Spread is too high -> SHORT
    
    # 3. The Exit Signals (The Zero-Crossing Trick)
    # How do we know without a loop if the Z-Score crossed 0? 
    # If yesterday was positive and today is negative, multiplying them gives a negative number.
    # We instantly find every single zero-crossing in the 5 years and stamp a 0 (Exit).
    positions[(z_score * z_score.shift(1)) <= 0] = 0
    
    # 4. Fill in the blanks (State Management)
    # ffill() means "Forward Fill". It takes our signals and carries them forward 
    # through time until it hits a new signal, perfectly simulating holding a trade.
    positions = positions.ffill().fillna(0)
    
    # --- CALCULATING THE MONEY ---
    # Shift positions by 1 day because you earn TOMORROW'S return on TODAY'S closing position
    positions_shifted = positions.shift(1).fillna(0)
    
    # Convert our dynamic hedge ratio list to a pandas series to match dates
    hr_series = pd.Series(dynamic_hr, index=y_clean.index)
    hr_shifted = hr_series.shift(1).fillna(0)
    
    # Daily Strategy Return = Position * (Return of Y - (Hedge Ratio * Return of X))
    strategy_daily_returns = positions_shifted * (y_returns.values - (hr_shifted.values * x_returns.values))
    
    # Calculate the Equity Curve (Starting with $1 and compounding)
    equity_curve = (1 + strategy_daily_returns).cumprod()
    
    print("-> Accountant: PnL calculation complete.")
    return strategy_daily_returns, equity_curve

def calculate_scorecard(daily_returns, equity_curve):
    """
    Calculates the final Sharpe Ratio and Max Drawdown to prove the system works.
    """
    print("-> Accountant: Generating final scorecard...")
    
    # 1. Sharpe Ratio (Assuming 252 trading days in a year)
    mean_return = np.mean(daily_returns)
    std_return = np.std(daily_returns)
    
    if std_return == 0:
        sharpe_ratio = 0
    else:
        # Annualize the Sharpe Ratio
        sharpe_ratio = (mean_return / std_return) * np.sqrt(252)
        
    # 2. Maximum Drawdown (The biggest peak-to-valley drop in our account)
    rolling_max = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - rolling_max) / rolling_max
    max_drawdown = np.min(drawdowns)
    
    return sharpe_ratio, max_drawdown

def plot_equity_curve(dates, equity_curve, sharpe, drawdown, ticker_pair):
    """
    Generates the final visual proof: Your bank account balance over time.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(dates, equity_curve, color='green', linewidth=2, label='Strategy Equity')
    
    plt.title(f'Phase 3.5: Kalman Filter PnL ({ticker_pair})\nSharpe: {sharpe:.2f} | Max DD: {drawdown:.1%}', fontsize=14, fontweight='bold')
    plt.xlabel('Timeline', fontsize=12)
    plt.ylabel('Cumulative Return (Multiplier)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.fill_between(dates, equity_curve, 1.0, where=(equity_curve > 1.0), facecolor='green', alpha=0.1)
    plt.fill_between(dates, equity_curve, 1.0, where=(equity_curve < 1.0), facecolor='red', alpha=0.1)
    plt.legend()
    
    plt.savefig('kalman_equity_curve.png', dpi=300)
    print("-> SUCCESS: Equity curve saved as 'kalman_equity_curve.png'")

# --- MASTER EXECUTION ---
if __name__ == "__main__":
    print("\n=========================================")
    print(" Donna's Dynamic PnL Engine Initializing...")
    print("=========================================\n")
    
    y_ticker = "6E=F" # Euro
    x_ticker = "6B=F" # Pound
    
    # We use a solid baseline static ratio to kick off day 1
    initial_hr = 1.0402 
    half_life = 20.0 
    
    # 1. Pull the data (Using functions from project_3_main)
    y_raw = get_cleaned_data(y_ticker)
    x_raw = get_cleaned_data(x_ticker)
    y_clean, x_clean = align_assets(y_raw, x_raw)
    
    # 2. Run the Kalman Filter Brain
    kalman_hr, kalman_intercept = run_kalman_filter(y_clean, x_clean, initial_hedge_ratio=initial_hr)
    
    # 3. Calculate Spread and Z-Score
    dynamic_spread = calculate_dynamic_spread(y_clean, x_clean, kalman_hr, kalman_intercept)
    z_score = calculate_dynamic_zscore(dynamic_spread, half_life)
    
    # 4. Count the Money (Phase 3.5 Logic)
    daily_returns, equity_curve = calculate_backtest_pnl(y_clean, x_clean, kalman_hr, z_score)
    
    # 5. Generate the Scorecard
    sharpe, max_dd = calculate_scorecard(daily_returns, equity_curve)
    print(f"\n=========================================")
    print(f" FINAL SCORECARD: {y_ticker} vs {x_ticker}")
    print(f" Sharpe Ratio: {sharpe:.2f}")
    print(f" Max Drawdown: {max_dd:.1%}")
    print("=========================================\n")
    
    # 6. Plot the Equity Curve
    plot_equity_curve(y_clean.index, equity_curve, sharpe, max_dd, f"{y_ticker} / {x_ticker}")