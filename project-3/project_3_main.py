import yfinance as yf
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import numpy as np
import math
import sys


def getCloseData(inTicker):
    rawData = yf.download(inTicker, period="5y", interval="1d", auto_adjust=True)
    closeData = rawData['Close']
    cleanedClose_Data = closeData.dropna()
    return cleanedClose_Data

def checkPointTwo(len1, len2):
    if(len1 == len2):
        print("Check point 2 passed")
    else:
        sys.exit(f"Checkpoint 2 of project 2 failed. Exit Code: {EXIT_CODE_22}")
        
def getSpread(asset_y, asset_x, hedge_ratio):
    
    hr = hedge_ratio
    
    yCD = getCloseData(asset_y)
    xCD = getCloseData(asset_x)
    
    # checkpoint 2
    # check the length of asset y and asset x
    lenY = len(yCD)
    lenX = len(xCD)
    checkPointTwo(lenY, lenX)
    
    spread = np.log(yCD[asset_y] - (hr*np.log(xCD[asset_x])))
    # spread = spread.to_frame()
    return spread

def getSTD(spread, half_life):
    # checkpoint 1
    # check if the half-life is greater than 2
    if half_life < 2:
        half_life == 2
    
    hl = round(half_life)

    # print(type(spread))
    std_arr = spread.rolling(window = hl, min_periods = hl).std()
    
        
    return std_arr

# reading in data
csvProject_1 = pd.read_csv('../project-1/project_1_Output.csv')
csvProject_2 = pd.read_csv('../project-2/project_2_Output.csv')
initAssets = csvProject_1.iloc[2]
# print(initAssets.Hedge_Ratio)

Asset_y = getCloseData(initAssets.Asset_y)
Asset_x = getCloseData(initAssets.Asset_x)
checkPointTwo(len(Asset_y), len(Asset_x))
spread = getSpread(initAssets.Asset_y, initAssets.Asset_x, initAssets.Hedge_Ratio)
rollSTD = getSTD(spread, initAssets.Half_Life)
# Q = process variance. represents the natural, slow drift of the market.
Q = 0.0001
# R = getSTD(initAssets.Asset_y)^2 = measurement variance
R = rollSTD * rollSTD
# initial headge ratio is from project 1 until the program is up and running and then it'll be the yesterday value
predictedHR = initAssets.Hedge_Ratio + Q
KalGain = predictedHR/(predictedHR + R)
newHR = (1-KalGain) * predictedHR 
# print(getSpread(initAssets.Asset_y, initAssets.Asset_x, initAssets.Hedge_Ratio))
print(R)