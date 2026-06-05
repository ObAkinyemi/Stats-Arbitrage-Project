import yfinance as yf
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import numpy as np
import math
import sys


# first digit = the project number
# 2nd digit corresponds to function
# 2 = project 2
# 1 = checkpoint 1
EXIT_CODE_21 = 21 #checkpoint 1 failed
EXIT_CODE_22 = 22 #checkpoint 2 failed
csvFile = pd.read_csv('../project-1/project_1_Output.csv')

def checkPointOne(closeData, ticker):
    # create data frame for ticker
    tickerIndices = np.array(closeData.index)
    tickerColumns = np.array(closeData.columns)
    tickerVals = np.array(closeData.values)
    
    tickerData = pd.DataFrame(data = tickerVals, index = tickerIndices, columns = tickerColumns)
    
    # check for nan values
    nanMask = set()
    nanIndex = 0
    
    for value in tickerData[ticker]:
        if (np.isnan(value) and len(nanMask) == 0):
            rowToDrop = tickerData[ticker].index[nanIndex]
            nanMask.add(rowToDrop)
            nanIndex += 1
    
    # turn the set into a list
    nanMaskList = [*nanMask]
    
    # extracting date information from the nanIndex obtained in the above for loop
    # and turning it into a string to input as a key into the data frame.
    print("\n")
    for data in nanMaskList:
        dataYear = "{:02d}".format(data.date().year)
        dataMonth = "{:02d}".format(data.date().month)
        dataDay = "{:02d}".format(data.date().day)
        stringifiedDate = f"{dataYear}-{dataMonth}-{dataDay}"
        tickerData.drop([stringifiedDate], inplace = True)
        
    return tickerData
    
def checkPointTwo(len1, len2):
    if(len1 == len2):
        print("Check point 2 passed")
    else:
        sys.exit(f"Checkpoint 2 of project 2 failed. Exit Code: {EXIT_CODE_22}")

def createEquityCurve(daily_profits):
    
    return daily_profits.cumsum()
        

def create_drawdown(equity_curve):
    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index = eq_idx, dtype=float)
    duration = pd.Series(index = eq_idx, dtype=float)

    # Loop over the index range
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], equity_curve.iloc[t])
        hwm.append(cur_hwm)
        drawdown.iloc[t]= hwm[t] - equity_curve.iloc[t]
        duration.iloc[t]= 0 if drawdown.iloc[t] == 0 else duration.iloc[t-1] + 1
    return drawdown.max(), duration.max()

def getCloseData(ticker):
    rawData = yf.download(tickers=ticker, period="2y", interval="1d", auto_adjust=True)
    closeData = rawData['Close']
    return closeData

def getSpread(asset_y, asset_x, hedge_ratio):
    
    hr = hedge_ratio
    
    yCD = checkPointOne(getCloseData(asset_y), asset_y)
    xCD = checkPointOne(getCloseData(asset_x), asset_x)
    
    # checkpoint 2
    # check the length of asset y and asset x
    lenY = len(yCD)
    lenX = len(xCD)
    checkPointTwo(lenY, lenX)
    
    spread = np.log(yCD[asset_y]) - (hr*np.log(xCD[asset_x]))
    # spread = spread.to_frame()
    return spread
    
def getSMA(spread, half_life):

    # checkpoint 1
    # check if the half-life is greater than 2
    if half_life < 2:
        half_life == 2
    
    hl = round(half_life)
    # print(type(spread))
    sma_arr = spread.rolling(window = hl, min_periods = hl).mean()
    
    # print(len(sma_arr))
        
    return sma_arr
            
def getSTD(spread, half_life):
    # checkpoint 1
    # check if the half-life is greater than 2
    if half_life < 2:
        half_life == 2
    
    hl = round(half_life)

    # print(type(spread))
    std_arr = spread.rolling(window = hl, min_periods = hl).std()
    
        
    return std_arr
    
    
project2Results = []
# for loop to go through all the data points. Figure it out after doing the mark down ratio thingy.
    
for row in csvFile.itertuples():
    yTicker = row.Asset_y
    xTicker = row.Asset_x
    hedgeRatio = row.Hedge_Ratio
    halfLife = float(row.Half_Life)

    spr = getSpread(yTicker, xTicker, hedgeRatio)
    sma = getSMA(spr, halfLife)
    std = getSTD(spr, halfLife)

    # print(f"type of spread: {type(spr)}")
    # print(f"type of sma: {type(sma)}")
    # print(f"type of stdev: {type(std)}")

    # print(spr)
    # print(sma)
    # print(std)

    z_Score = (spr-sma)/std
    print(z_Score)

    state = 0

    position = pd.Series(data = [0 for i in range(len(z_Score))], index = z_Score.index, dtype="int8")
    for i in range(len(z_Score)):
        
        val = z_Score.values[i]
        
        # exit
        if state == -1 and val <= 0:
            state = 0
        
        if state == 1 and val >= 0:
            state = 0
        
        # entry
        if val >= 2 and state == 0:
            # short asset y and buy asset x. I.e short the spread
            # print(f"{i} : {z_Score.index[i]} : {z_Score.values[i]}")
            state = -1
            # positions.iloc[i] = 1 or something
        elif val <= -2 and state == 0:
            # short asset x and buy asset y. I.e. buy the spread
            # print(f"{i} : {z_Score.index[i]} : {z_Score.values[i]}")
            state = 1
        
        position.iloc[i] = state
            

    spread_change = spr.diff()
    spread_change.dropna(inplace=True)
    new_position = position.shift(1)

    payoff = spread_change*new_position 
    total_profit = payoff.sum()
    # print(f"total profit: {total_profit}")

    # Sharpe Ratio: (Mean of Daily Returns (meanDR)/ Standard Deviation of Daily Returns (stdevDR)) * math.sqrt(252)
    meanDR = payoff.mean()
    stdevDR = payoff.std()
    Sharpe_Ratio = (meanDR/stdevDR)*math.sqrt(252)
    # print(f"Sharpe Ratio: {Sharpe_Ratio}")


    # Max Drawdown: a little more complex

    # equity curve
    # print(payoff)
    eqCurve = createEquityCurve(payoff)

    # create_drawdown(eqCurve)
    # high water mark
    # MDD
    max_dd, max_duration = create_drawdown(eqCurve)

        
    # drawdown
    print(f"Max Drawdown: {max_dd}")

    pair_stats = {
        "Asset_y": yTicker,
        "Asset_x": xTicker,
        "Sharpe": Sharpe_Ratio,
        "Max_Drawdown": max_dd
    }
    project2Results.append(pair_stats)
    
print("results")
# print(project2Results)
project_2_DF = pd.DataFrame(data=project2Results)
print(project_2_DF)
project_2_DF.to_csv("project_2_Output.csv", index=False)