import yfinance as yf
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import numpy as np
import csv

csvFile = pd.read_csv('../project-1/project_1_Output.csv')


def getCloseData(ticker):
    rawData = yf.download(tickers=ticker, period="2y", interval="1d", auto_adjust=True)
    closeData = rawData['Close']
    return closeData

def getSpread(asset_y, asset_x, hedge_ratio):
    
    yCD = getCloseData(asset_y)
    xCD = getCloseData(asset_x)
    hr = hedge_ratio
    
    # print(yCD['ES=F'].iloc[0])
    # checkpoint 1
    # checkpoint 2
    # check the length of asset y and asset x
    len_close = len(yCD)-1 #temporary until check length is implemented
    
    spread = np.log(yCD[asset_y]) - (hr*np.log(xCD[asset_x]))
    print(spread)
    
            
    
def getSMA(spread, half_life):

    # checkpoint 1
    # check if the half-life is greater than 2
    # rounding function to round the half life up or down based on what it is.
    
    hl = half_life
    len_spread = len(spread)

    sma_arr = np.array([], dtype= 'd')
    
    for n in range(0, len_spread):
        sum = 0
        for i in range(n, n+hl):
            sum += spread.iloc[0]
            avg = sum/hl
        
        np.append(sma_arr, avg)
        
    return sma_arr
            
    
# print(getCloseData('ES=F'))

yTicker = csvFile['Asset y'][0]
xTicker = csvFile['Asset x'][0]
hedgeRatio = csvFile['Hedge_Ratio'][0]
getSpread(yTicker, xTicker, hedgeRatio)

halfLife = csvFile['Half_Life'][0]

# simple moving average
# period = half_life
# get n price points and divide it over n for each period
# spread_arr = []
# spread = getCloseData(asset_x)[i] - (hedge_ratio*getcloseData(asset_y)[i])

# checkpoint 1
# checkpoint 2
# for loop
    # spread_arr.append(spread)
    


# standard deviation

# Z-score = (spread (i.e. residuals) - rolling average)/rolling standard deviation


# bool buy_flag = false
# bool sell_flag = false
# entry/exit

# zscore trade for above 2.0 (sell)
# zscore trade for below 2.0 (buy)
    
# sharpe and drawdown