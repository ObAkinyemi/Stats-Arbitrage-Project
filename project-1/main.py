import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
import csv


tickerList = ['ES=F', 'YM=F', 'CL=F', 'NG=F', 'GC=F', 'HG=F', '6E=F', '6J=F', 'ZB=F', 'ZN=F']
tickerList_short = ['ES=F', 'YM=F']
# auto_adjust = true gives me all the adjusted close data (I think)
rawData = yf.download(tickers=tickerList_short, period="2y", interval="1d", auto_adjust=True)
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
        
#             for k in range(0, len(rawClose)-495):
#                 # print(f"{rawData['Close'][tickerList[i]].iloc[k]} vs {rawData['Close'][tickerList[j]].iloc[k]}")
#                 writer.writerow([rawData['Close'][tickerList[i]].iloc[k], rawData['Close'][tickerList[j]].iloc[k]])

# print(closeData['ES=F'].tolist())
# print(closeData['YM=F'].tolist())

x = closeData['ES=F'].tolist()
y = closeData['YM=F'].tolist()

x_log = np.log(x)
y_log = np.log(y)
x_log = sm.add_constant(x_log)


result = sm.OLS(y_log, x_log).fit()
# print(result.summary())
# print(result.params[1])

# residual values
residuals = result.resid
print(len(result.resid))
print(type(result.resid))

# ADF test to get p-value
ADF_test = sm.adfuller(residuals)
print(ADF_test.summary())

# slope is hedge ratio = results.params[1]
# p_value comes from using the residuals from OLS in the ADF


plt.scatter(np.log(closeData['ES=F']), np.log(closeData['YM=F']), color='blue', label='Data Points')

x_range = np.linspace(np.log(closeData['ES=F']).min(), np.log(closeData['ES=F']).max(), 100)
y_pred = result.params[0] + result.params[1] * x_range 

plt.plot(x_range, y_pred, color='red', label='Regression Line')
plt.xlabel('Independent Variable (X)')
plt.ylabel('Dependent Variable (Y)')
plt.title('OLS Regression Fit')
plt.legend()
plt.show()
