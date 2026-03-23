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
    
    len_close = len(yCD)-1 #temporary until check length is implemented
    
    spread = np.log(yCD[asset_y]) - (hr*np.log(xCD[asset_x]))
    return spread
    
            
    
def getSMA(spread, half_life):

    # checkpoint 1
    # check if the half-life is greater than 2
    if half_life < 2:
        half_life == 2
    
    hl = round(half_life)
    len_spread = len(spread)
    dfSpread = spread.to_frame()

    print(type(dfSpread))
    sma_arr = dfSpread.rolling(window = hl, min_periods = hl).mean()
    
    # print(len(sma_arr))
        
    return sma_arr
            
def getSTD(spread, half_life):
        # checkpoint 1
    # check if the half-life is greater than 2
    if half_life < 2:
        half_life == 2
    
    hl = round(half_life)
    dfSpread = spread.to_frame()

    print(type(dfSpread))
    std_arr = dfSpread.rolling(window = hl, min_periods = hl).std()
    
    # print(len(sma_arr))
        
    return std_arr
    
# print(getCloseData('ES=F'))

yTicker = csvFile['Asset y'][0]
xTicker = csvFile['Asset x'][0]
hedgeRatio = csvFile['Hedge_Ratio'][0]
halfLife = float(csvFile['Half_Life'][0])

spr = getSpread(yTicker, xTicker, hedgeRatio)
print(spr)
sma = getSMA(spr, halfLife)
std = getSTD(spr, halfLife)
print(sma)
print(std)

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