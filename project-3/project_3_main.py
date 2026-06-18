import os
import sys
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Exit Codes for clean debugging
EXIT_CODE_SUCCESS = 0
EXIT_CODE_ALIGN_FAILED = 31

def get_cleaned_data(ticker):
    """
    Downloads 5 years of daily close data from Yahoo Finance.
    Drops any empty rows so our math doesn't trip on invisible potholes.
    """
    print(f"-> Pulling data for {ticker}...")
    raw_data = yf.download(ticker, period="5y", interval="1d", auto_adjust=True)
    return raw_data['Close'].dropna()

def align_assets(y_series, x_series):
    """
    Matches the dates for both assets perfectly. If Asset Y traded on a Tuesday 
    but Asset X was closed, it deletes Tuesday so the rows match exactly.
    """
    print("-> Aligning dates for both assets...")
    aligned_df = pd.concat([y_series, x_series], axis=1, join='inner')
    aligned_df.columns = ['Asset_Y', 'Asset_X']
    return aligned_df['Asset_Y'], aligned_df['Asset_X']

def run_kalman_filter(y_prices, x_prices, initial_hedge_ratio=1.0):
    """
    THE BRAIN: 
    Calculates the changing Hedge Ratio (slope) and Intercept (gap) for every single day.
    """
    print("-> Starting Kalman Filter time machine...")
    
    y = np.log(y_prices.values)
    x = np.log(x_prices.values)
    n_days = len(y)
    
    # theta holds our current estimates: [Hedge Ratio, Intercept]
    theta = np.zeros((2, n_days))
    theta[:, 0] = [initial_hedge_ratio, 0.0]
    
    P = np.eye(2) # Uncertainty Meter (Our Doubt)
    Q = np.eye(2) * 1e-4 # Market Drift (Caffeine intake / How fast things change)
    R = 1e-3 # Measurement Noise (Market Static)
    
    dynamic_hedge_ratios = []
    dynamic_intercepts = []
    
    for t in range(n_days):
        current_x = x[t]
        current_y = y[t]
        
        # H is how we set up the scale to weigh our guess against reality
        H = np.array([current_x, 1.0]).reshape(1, 2)
        
        # 1. Morning Guess
        if t > 0:
            theta_pred = theta[:, t-1]
        else:
            theta_pred = theta[:, 0]
            
        P_pred = P + Q
        
        # 2. Check Reality
        y_pred = np.dot(H, theta_pred)[0]
        error = current_y - y_pred # How wrong was our guess?
        
        S = np.dot(H, np.dot(P_pred, H.T))[0, 0] + R
        K = np.dot(P_pred, H.T) / S # The Blender percentage (Kalman Gain)
        
        # 3. Dynamic Update (Adjusting our beliefs)
        theta_current = theta_pred + K.flatten() * error
        theta[:, t] = theta_current
        
        # Shrink our doubt because we saw real data today
        P = (np.eye(2) - np.dot(K, H)) * P_pred
        
        dynamic_hedge_ratios.append(theta_current[0])
        dynamic_intercepts.append(theta_current[1])
        
    print("-> Kalman Filter processing complete!")
    return dynamic_hedge_ratios, dynamic_intercepts

def calculate_dynamic_spread(y_prices, x_prices, dynamic_hr, dynamic_intercept):
    """
    THE STEERING WHEEL:
    Calculates the spread day-by-day using the changing Kalman numbers.
    Formula: ln(Y) - (beta * ln(X) + alpha)
    """
    print("-> Calculating Dynamic Spread...")
    
    # Put both assets on the scale (take the natural logs)
    y_log = np.log(y_prices.values)
    x_log = np.log(x_prices.values)
    
    # Convert our Kalman lists into high-speed math arrays
    beta = np.array(dynamic_hr)
    alpha = np.array(dynamic_intercept)
    
    # The actual subtraction. NO outer log() wrapper! 
    # We subtract the weighted X AND the intercept to keep the spread perfectly centered.
    dynamic_spread = y_log - (beta * x_log + alpha)
    
    # Return it as a Pandas series so the dates stay attached
    return pd.Series(dynamic_spread, index=y_prices.index)

def calculate_dynamic_zscore(dynamic_spread, half_life):
    """
    THE BRAKES (AND THE GAS):
    Calculates how far the spread is stretching from its moving average.
    """
    print(f"-> Calculating Rolling Z-Score (Window: {half_life} days)...")
    
    # Safety Check: If half-life is too small, force it to be at least 2 days
    window = max(2, int(round(half_life)))
    
    # Find the moving average (Where should the price be?)
    rolling_mean = dynamic_spread.rolling(window=window).mean()
    
    # Find the moving standard deviation (How bouncy is the price normally?)
    rolling_std = dynamic_spread.rolling(window=window).std()
    
    # Calculate Z-Score: (Today's Spread - Average Spread) / Normal Bounce Size
    z_score = (dynamic_spread - rolling_mean) / rolling_std
    
    return z_score

def plot_trading_signals(dates, z_score, y_ticker, x_ticker):
    """
    Generates the final visual dashboard showing exactly when the bot 
    should pull the trigger on a trade.
    """
    print("-> Generating Trading Signals Chart...")
    plt.figure(figsize=(12, 6))
    
    # Plot the living Z-Score
    plt.plot(dates, z_score, color='purple', label='Dynamic Z-Score', linewidth=1.5)
    
    # Draw our Trigger Lines (The Red/Green lights)
    plt.axhline(y=2.0, color='red', linestyle='--', label='Short Trigger (+2.0)')
    plt.axhline(y=-2.0, color='green', linestyle='--', label='Long Trigger (-2.0)')
    plt.axhline(y=0.0, color='black', linestyle='-', alpha=0.5, label='Exit (Zero Line)')
    
    plt.title(f'Project 3: Kalman Execution Signals ({y_ticker} vs {x_ticker})', fontsize=14, fontweight='bold')
    plt.xlabel('Timeline', fontsize=12)
    plt.ylabel('Standard Deviations (Z-Score)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11)
    
    plt.savefig('kalman_trading_signals.png', dpi=300)
    print("-> SUCCESS: Chart saved as 'kalman_trading_signals.png'")

# --- MASTER SCRIPT EXECUTION ---
if __name__ == "__main__":
    print("\n=========================================")
    print(" Donna's Kalman Filter Initializing...")
    print("=========================================\n")
    
    y_ticker = "6E=F" # Euro Futures
    x_ticker = "6B=F" # British Pound Futures
    
    # --- ABSOLUTE PATHING FIX (The GPS) ---
    # Find exactly where this Python script lives on the hard drive
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Build a bulletproof map to the Project 1 folder
    csv_path = os.path.join(script_directory, '..', 'project-1', 'project_1_Output.csv')
    csv_path = os.path.normpath(csv_path) # Cleans up the path format
    
    print(f"-> Hunting for CSV file at: {csv_path}")
    
    try:
        project_1_data = pd.read_csv(csv_path)
        
        # Using exact spelling (Asset_y and Asset_x) to bypass your spelling error trap
        target_pair = project_1_data[
            (project_1_data['Asset_y'] == y_ticker) & (project_1_data['Asset_x'] == x_ticker)
        ]
        
        if len(target_pair) > 0:
            static_hr = float(target_pair['Hedge_Ratio'].values[0])
            
            # Try to grab the half-life. If it's missing from your CSV, default to 20 days.
            try:
                half_life = float(target_pair['Half_Life'].values[0])
            except KeyError:
                half_life = 20.0
                print("-> Notice: 'Half_Life' column not found in CSV. Using default 20 days.")
                
            print(f"-> Found Data! Starting HR: {static_hr:.4f} | Half-Life: {half_life:.2f} days")
        else:
            raise ValueError("Ticker pair not found in CSV.")
            
    except Exception as e:
        print(f"-> Notice: Could not read CSV ({e}). Using defaults.")
        static_hr = 1.0402
        half_life = 20.0 # Default fallback window
    
    # 1. Get and align data
    y_raw = get_cleaned_data(y_ticker)
    x_raw = get_cleaned_data(x_ticker)
    y_clean, x_clean = align_assets(y_raw, x_raw)
    
    if len(y_clean) != len(x_clean) or len(y_clean) == 0:
        print("Error: Asset data length alignment failed.")
        sys.exit(EXIT_CODE_ALIGN_FAILED)
        
    # 2. Run the Brain (Kalman Filter)
    kalman_hr, kalman_intercept = run_kalman_filter(y_clean, x_clean, initial_hedge_ratio=static_hr)
    
    # 3. Grab the Steering Wheel (Dynamic Spread)
    dynamic_spread = calculate_dynamic_spread(y_clean, x_clean, kalman_hr, kalman_intercept)
    
    # 4. Hit the Brakes/Gas (Dynamic Z-Score)
    dynamic_z_score = calculate_dynamic_zscore(dynamic_spread, half_life)
    
    # 5. Output the final trading signals chart
    plot_trading_signals(y_clean.index, dynamic_z_score, y_ticker, x_ticker)
    
    print("\n=========================================")
    print(" Project 3 Execution Complete. Trade Ready.")
    print("=========================================\n")
    sys.exit(EXIT_CODE_SUCCESS)