import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import math
# Exit Codes for structural tracking
EXIT_CODE_SUCCESS = 0
EXIT_CODE_ALIGN_FAILED = 31

def get_cleaned_data(ticker):
    """
    Downloads 5 years of daily close data from Yahoo Finance 
    and drops any empty NaN values to keep the dataset clean.
    """
    raw_data = yf.download(ticker, period="5y", interval="1d", auto_adjust=True)
    close_series = raw_data['Close']
    return close_series.dropna()

def align_assets(y_series, x_series):
    """
    Ensures both asset price series have the exact same dates.
    If one asset traded on a day the other didn't, we drop that day.
    """
    aligned_df = pd.concat([y_series, x_series], axis=1, join='inner')
    aligned_df.columns = ['Asset_Y', 'Asset_X']
    return aligned_df['Asset_Y'], aligned_df['Asset_X']

def run_kalman_filter(y_prices, x_prices, initial_hedge_ratio=1.0):
    """
    The heart of Project 3: The Kalman Filter.
    This steps through time day-by-day, adjusting the Hedge Ratio and 
    Intercept dynamically as price updates roll in.
    
    State Vector (theta): [Hedge_Ratio, Intercept]^T
    Measurement: y_t = Hedge_Ratio * x_t + Intercept + noise
    """
    # Convert series to plain numpy arrays for high-speed processing
    y = np.log(y_prices.values)
    x = np.log(x_prices.values)
    n_days = len(y)
    
    # --- STEP 1: INITIALIZE THE PARAMETERS ---
    # We track two hidden states: the moving Hedge Ratio (slope) and the Intercept (offset)
    # theta holds our current estimates: [Hedge Ratio, Intercept]
    theta = np.zeros((2, n_days))
    theta[:, 0] = [initial_hedge_ratio, 0.0]  # Start with our Project 1 static guess
    
    # P is our Uncertainty Covariance Matrix (our State Doubt Meter)
    # We start with highly uncertain guesses (1.0 variance)
    P = np.eye(2)
    
    # Q is our Process Variance (The drift parameter we discussed)
    # This represents how fast the true relationship is allowed to adapt over time
    Q = np.eye(2) * 1e-4  # Tuned microscopic Q for smooth, realistic tracking
    
    # R is our Measurement Variance (The daily market static/noise expectation)
    # We assume a fixed level of standard market volatility noise
    R = 1e-3
    
    # Arrays to store the outputs of our daily run
    dynamic_hedge_ratios = []
    dynamic_intercepts = []
    
    # --- STEP 2: THE CHRONOLOGICAL "TIME MACHINE" LOOP ---
    for t in range(n_days):
        # Current prices for the day
        current_x = x[t]
        current_y = y[t]
        
        # Define the measurement vector H_t = [x_t, 1]
        H = np.array([current_x, 1.0]).reshape(1, 2)
        
        # A. Prediction Phase (The Morning Guess)
        # Yesterday's final estimate becomes today's morning guess
        if t > 0:
            theta_pred = theta[:, t-1]
        else:
            theta_pred = theta[:, 0]
            
        # Our uncertainty grows slightly overnight due to the passage of time
        P_pred = P + Q
        
        # B. Measurement Update Phase (Checking Reality)
        # Calculate the predicted price of Y based on our morning guess
        y_pred = np.dot(H, theta_pred)[0]
        
        # Calculate the error (Innovation)
        error = current_y - y_pred
        
        # Calculate the variance of our prediction error
        S = np.dot(H, np.dot(P_pred, H.T))[0, 0] + R
        
        # Calculate the Kalman Gain (How much of the error we should absorb)
        K = np.dot(P_pred, H.T) / S
        
        # C. Correction Phase (The Dynamic Update)
        # Adjust our beliefs based on the Kalman Gain and the error
        theta_current = theta_pred + K.flatten() * error
        theta[:, t] = theta_current
        
        # Update our Uncertainty Covariance Matrix (our doubt shrinks because we saw real data)
        P = (np.eye(2) - np.dot(K, H)) * P_pred
        
        # Save our shiny new daily parameters
        dynamic_hedge_ratios.append(theta_current[0])
        dynamic_intercepts.append(theta_current[1])
        
    return dynamic_hedge_ratios, dynamic_intercepts

def generate_comparison_chart(dates, static_hr, dynamic_hr, y_ticker, x_ticker):
    """
    Creates and saves the ultimate comparison visual: Static vs. Kalman
    """
    plt.figure(figsize=(12, 6))
    
    # Plot the flat static line from Project 1/2
    plt.axhline(y=static_hr, color='red', linestyle='--', label=f'Static Hedge Ratio ({static_hr:.4f})', alpha=0.8)
    
    # Plot the living, waving Kalman curve
    plt.plot(dates, dynamic_hr, color='dodgerblue', label='Dynamic Kalman Hedge Ratio', linewidth=2)
    
    plt.title(f'Project 3: Static vs. Kalman Dynamic Hedge Ratio ({y_ticker} vs {x_ticker})', fontsize=14, fontweight='bold')
    plt.xlabel('Timeline', fontsize=12)
    plt.ylabel('Hedge Ratio Value (Slope)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(fontsize=11)
    
    # Save chart to disk
    plt.savefig('static_vs_kalman_comparison.png', dpi=300)
    print("SUCCESS: Comparison chart generated and saved as 'static_vs_kalman_comparison.png'")

# --- MASTER SCRIPT EXECUTION ---
if __name__ == "__main__":
    print("Donna's Kalman Filter Initializing...")
    
    # Target Tickers (Your star pair from Project 2)
    y_ticker = "6E=F" # Euro Futures
    x_ticker = "6B=F" # British Pound Futures
    
    # Step 1: Grab static hedge ratio from Project 1 output
    try:
        project_1_data = pd.read_csv('../project-1/project_1_Output.csv')
        # Filter for our target pair
        target_pair_row = project_1_data[
            (project_1_data['Asset_y'] == y_ticker) & (project_1_data['Asset_x'] == x_ticker)
        ]
        
        if len(target_pair_row) > 0:
            static_hedge_ratio = float(target_pair_row['Hedge_Ratio'].values[0])
            print(f"Loaded Project 1 static hedge ratio: {static_hedge_ratio:.4f}")
        else:
            static_hedge_ratio = 1.0402  # Solid default from Project 2 scoreboard metadata
            print(f"Warning: Could not find pair in CSV. Using default static ratio: {static_hedge_ratio}")
    except Exception as e:
        static_hedge_ratio = 1.0402
        print(f"Notice: Loading default static ratio ({static_hedge_ratio}) due to CSV check: {e}")

    # Step 2: Download raw closing price data
    print(f"Downloading data for {y_ticker} and {x_ticker}...")
    y_raw = get_cleaned_data(y_ticker)
    x_raw = get_cleaned_data(x_ticker)
    
    # Step 3: Align dates to prevent time discrepancies (Safety Checkpoint)
    y_clean, x_clean = align_assets(y_raw, x_raw)
    
    if len(y_clean) != len(x_clean) or len(y_clean) == 0:
        print("Error: Asset data length alignment failed.")
        sys.exit(EXIT_CODE_ALIGN_FAILED)
        
    print(f"Data alignment successful. Total trading days: {len(y_clean)}")
    
    # Step 4: Run the Kalman Filter state-space model
    print("Running state-space updates...")
    kalman_ratios, kalman_intercepts = run_kalman_filter(y_clean, x_clean, initial_hedge_ratio=static_hedge_ratio)
    
    # Step 5: Generate the comparison chart (The Final Trophy)
    generate_comparison_chart(y_clean.index, static_hedge_ratio, kalman_ratios, y_ticker, x_ticker)
    
    print("Project 3 Execution complete. Engine standing by.")
    sys.exit(EXIT_CODE_SUCCESS)