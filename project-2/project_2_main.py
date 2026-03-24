import yfinance as yf
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import numpy as np
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
    
# def checkPointTwo(closeData1, closeData2):


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
    if(lenY == lenX):
        print("Check point 2 passed")
    else:
        sys.exit(f"Checkpoint 2 of project 2 failed. Exit Code: {EXIT_CODE_22}")
    
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
    
yTicker = csvFile['Asset y'][0]
xTicker = csvFile['Asset x'][0]
hedgeRatio = csvFile['Hedge_Ratio'][0]
halfLife = float(csvFile['Half_Life'][0])

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
        print(f"{i} : {z_Score.index[i]} : {z_Score.values[i]}")
        state = -1
        # positions.iloc[i] = 1 or something
    elif val <= -2 and state == 0:
        # short asset x and buy asset y. I.e. buy the spread
        print(f"{i} : {z_Score.index[i]} : {z_Score.values[i]}")
        state = 1
    
    position.iloc[i] = state
        
print(position)

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


# entry/exit

# zscore trade for above 2.0 (sell)
# zscore trade for below 2.0 (buy)
    
# sharpe and drawdown