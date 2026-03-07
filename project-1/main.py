import yfinance as yf
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import numpy as np
import csv


tickerList = ['ES=F', 'YM=F', 'CL=F', 'NG=F', 'GC=F', 'HG=F', '6E=F', '6J=F', 'ZB=F', 'ZN=F']
tickerList_short = ['ES=F', 'YM=F']
# auto_adjust = true gives me all the adjusted close data (I think)
rawData = yf.download(tickers=tickerList, period="2y", interval="1d", auto_adjust=True)
closeData = rawData['Close']
# print(DownloadedData)
# print(rawData['Close']['ES=F'])
# Close, Open, 
# print(rawData['Close'])

#loop through i (the tickers) done
# loop through j (the the comparative tickers)
# loop through k (the price data using iloc)
# DON'T CREATE 2D ARRAY OF TICKER DATA.
# WRITE CSV LIKE THIS Asset_1, Asset_2, P_Value, Hedge_Ratio, Half_Life
# CALCULATE ELSEWHERE AND THEN WRITE
# j != i
# create a dictionary with the following structure for all tickers.
# create all possible sets of 2
# ticker vs ticker:
    # [ticker1 data, ticker 2 data]
    
i = 0
j = 0

# this is the logic for the comparison
# for i in range(i, len(tickerList)):
# #     # print("Ticker i data: " + str(i) + str(closeData[tickerList[i]]))
    
#     for j in range(i+1,len(tickerList)-1):
# #         # Now loop through the price data using the length of the
#         # rawData['Close']['ES=F'].iloc[k] and pit the tickers against each other
       
#         print(f"ticker i: {tickerList[i]} vs ticker j: {tickerList[j]}")
#         with open('test.csv', 'a', newline='') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow([tickerList[i], tickerList[j]])
#             rawClose = rawData['Close'][tickerList[i]]
        

# print(closeData['ES=F'].tolist())
# print(closeData['YM=F'].tolist())

# raw logic of Engle-Granger ADF test

# calculating hedge ratio and getting residuals
# raw close data
x = closeData['ES=F'].tolist()
y = closeData['YM=F'].tolist()

# log'd close data for better consistency
x_log = np.log(x)
y_log = np.log(y)
x_log = sm.add_constant(x_log)


result = sm.OLS(y_log, x_log).fit()
# print(result.summary())

# the slope
# hedge_ratio = result.params[1]

# residual values (distance that each point is from the line)
residuals = result.resid

# calculating p value
# ADF test to get p-value
ts = pd.Series(residuals)
ADF_test = adfuller(residuals)
# print("p val")
# print(ADF_test[1])


# calculating half life
# create change array = todays spread - yesterdays spread (y-y1)
test = [1, 5, 16, 4, 2]
testDiff = np.diff(test)
# print(testDiff)
delta_spread_adj = np.diff(residuals)
# second list where all values are shifted forward by one. = yesterdays spread (y1)
past_spread = np.roll(residuals, 1)
mask = past_spread != past_spread[0]
new_past_spread = past_spread[mask]
# print(f"{len(delta_spread_adj)} vs {len(new_past_spread)}")
# OLS where y = change array (y-y1) and x = lagged array (y1)
hlx = new_past_spread
hly = delta_spread_adj
hlx = sm.add_constant(hlx)
hl_result = sm.OLS(hly, hlx).fit()
# print(hl_result.summary())
# extract the slope
hl_slope = hl_result.params[1]
hl = -(np.log(2))/hl_slope
# print(hl)




# residuals = result.resid
# slope is hedge ratio = result.params[1]
# p_value comes from using the residuals from OLS in the ADF = ADF_test[1]
# half life comes from using the residuals h1_result.params[1]

# master list
master_list = []

for i in range(i, len(tickerList)):
    for j in range(i+1,len(tickerList)-1):

    # smol list
        ivj = []
        ivj.append(tickerList[i])
        ivj.append(tickerList[j])
        
    # hedge ratio
        x = np.log(closeData[tickerList[i]].tolist())
        y = np.log(closeData[tickerList[j]].tolist())
        x = sm.add_constant(x)
        result = sm.OLS(y, x).fit()
        hedge_ratio = result.params[1]
        ivj.append(hedge_ratio)
    
    # residuals
        residuals = result.resid
        
    # p-value
        ADF_test = adfuller(residuals)
        p_val = ADF_test[1]
        
    # conditional logic
        if p_val < 0.05:
        
        # do all this
        
            ivj.append(p_val)
        
        # calculating half life
        
            # delta_y = todays spread - yesterdays spread
            delta_y = np.diff(residuals)

            # yesterdays spread
            past_spread = np.roll(residuals, 1)
            mask = past_spread != past_spread[0]
            n_past_spread = past_spread[mask]
            
            # implementing OLS regression on residuals to get half life
            hlx = n_past_spread
            hly = delta_y
            hlx = sm.add_constant(hlx)
            hl_result = sm.OLS(hly, hlx).fit()
            
            # extract the slope of the half life
            hl_slope = hl_result.params[1]
            
            # extract the half life
            hl = -(np.log(2))/hl_slope
            ivj.append(hl)
            master_list.append(ivj)
        
print(master_list)

for ivj in master_list:
    with open('test.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(ivj)

def getCloseData(tickerListArr):
    rawData = yf.download(tickers=tickerList, period="2y", interval="1d", auto_adjust=True)
    closeData = rawData['Close']
    return closeData

def masterListCreation(closeDataArr):
    master_list = []

    for i in range(i, len(tickerList)):
        for j in range(i+1,len(tickerList)-1):

        # smol list
            ivj = []
            ivj.append(tickerList[i])
            ivj.append(tickerList[j])
            
        # hedge ratio
            x = np.log(closeDataArr[tickerList[i]].tolist())
            y = np.log(closeDataArr[tickerList[j]].tolist())
            x = sm.add_constant(x)
            result = sm.OLS(y, x).fit()
            hedge_ratio = result.params[1]
            ivj.append(hedge_ratio)
        
        # residuals
            residuals = result.resid
            
        # p-value
            ADF_test = adfuller(residuals)
            p_val = ADF_test[1]
            
        # conditional logic
            if p_val < 0.05:
            
            # do all this
            
                ivj.append(p_val)
            
            # calculating half life
            
                # delta_y = todays spread - yesterdays spread
                delta_y = np.diff(residuals)

                # yesterdays spread
                past_spread = np.roll(residuals, 1)
                mask = past_spread != past_spread[0]
                n_past_spread = past_spread[mask]
                
                # implementing OLS regression on residuals to get half life
                hlx = n_past_spread
                hly = delta_y
                hlx = sm.add_constant(hlx)
                hl_result = sm.OLS(hly, hlx).fit()
                
                # extract the slope of the half life
                hl_slope = hl_result.params[1]
                
                # extract the half life
                hl = -(np.log(2))/hl_slope
                ivj.append(hl)
                master_list.append(ivj)
                
    return master_list

def writeToFile(outputFile, masterListArr):
    for ivj in masterListArr:
        with open('test.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(ivj)


# visualize the data if wanted. This is for ES=F and YM=F
# plt.scatter(np.log(closeData['ES=F']), np.log(closeData['YM=F']), color='blue', label='Data Points')

# x_range = np.linspace(np.log(closeData['ES=F']).min(), np.log(closeData['ES=F']).max(), 100)
# y_pred = result.params[0] + result.params[1] * x_range 

# plt.plot(x_range, y_pred, color='red', label='Regression Line')
# plt.xlabel('Independent Variable (X)')
# plt.ylabel('Dependent Variable (Y)')
# plt.title('OLS Regression Fit')
# plt.legend()
# plt.show()
