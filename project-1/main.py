import yfinance as yf
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import numpy as np
import csv


tickerList = [
              ['ES=F', 'NQ=F', 'RTY=F', 'NKD=F', 'YM=F'],
              ['ZT=F', 'ZF=F', 'ZN=F', 'ZB=F', 'TN=F', 'ZQ=F'],
              ['CL=F', 'NG=F', 'BZ=F', 'HO=F', 'RB=F'],
              ['GC=F', 'HG=F', 'SI=F', 'PL=F', 'PA=F', 'ALI=F'],
              ['6E=F', '6J=F', '6B=F', '6A=F', '6C=F', '6N=F'],
              ['ZC=F', 'ZW=F', 'ZS=F', 'ZM=F', 'ZL=F', 'ZO=F'],
              ]
zipperTest = ['ZC=F','ZF=F','RTY=F','PL=F']

# get the close data needed
def getCloseData(tickerListArr):
    rawData = yf.download(tickers=tickerListArr, period="5y", interval="1d", auto_adjust=True)
    closeData = rawData['Close']
    return closeData

# create the 2D arr of the data necessary
# tickerRow is the row of tickers for this asset class
# closeDataArr is the close data informatoin
def ivjListCreation(closeDataArr, tickerRow):
    
    
    
    # CheckPoint 1: filter the data by dates *now unecessary*
    myDataIndices = np.array(closeDataArr.index)
    myDataColumns = np.array(closeDataArr.columns)
    myDataVals = np.array(closeDataArr.values)
    
    myData = pd.DataFrame(data = myDataVals, index = myDataIndices, columns = myDataColumns)

    
    
    # Checkpoint 1*: filter the data by Nan
    # This is to make sure I don't feed the math thingy nan data and
    # then it breaks because it got something it can't use (like nan).
    myData.dropna(inplace = True)
        
    print(f"-------------------------- Check Point 1 Passed --------------------------")

    # Checkpoint 2*: filter the data by number of data points
    # you will drop the column that doesn't have enough data points!!!!
    # lenMaskIndices
    for ticker in tickerRow:
        if len(myData[ticker]) < 300:
            myData.drop(columns=[ticker])
     
    print(f"-------------------------- CheckPoint 2 Passed --------------------------")
   
    masterList = []

    for i in range(0, len(tickerRow)):
        for j in range(i+1,len(tickerRow)-1):
            
            print(f"-------------------------- {tickerRow[i]} vs {tickerRow[j]} --------------------------")
    #     # smol list
            ivj = []
            
            ivj.append(tickerRow[i])
            ivj.append(tickerRow[j])
            print(f"-------------------------- ivj appended --------------------------")
            
            
    #     # hedge ratio
            x = np.log(myData[tickerRow[i]].tolist())
            y = np.log(myData[tickerRow[j]].tolist())
            x = sm.add_constant(x)
            result = sm.OLS(y, x).fit()
            hedge_ratio = result.params[1]
            ivj.append(hedge_ratio)
        
            print(f"-------------------------- hedge ratio appended --------------------------")
    #     # residuals/spread
            residuals = result.resid
            
    #     # p-value
            ADF_test = adfuller(residuals)
            p_val = ADF_test[1]
            
            print(f"-------------------------- adfuller test passed appended --------------------------")
    #     # conditional logic
            if p_val < 0.05:
            
    #         # do all this
            
                ivj.append(p_val)
            
                print(f"-------------------------- pval appended --------------------------")
    #         # calculating half life
            
                # delta_y = todays spread - yesterdays spread
                delta_y = np.diff(residuals)
                print(f"-------------------------- delta y calculated --------------------------")

    #             # yesterdays spread
                past_spread = np.roll(residuals, 1)
                mask = past_spread != past_spread[0]
                n_past_spread = past_spread[mask]
                print(f"-------------------------- past spread calculated --------------------------")
                print(f"length of past spread arr: {len(n_past_spread)}")
                print(f"length of delta y arr: {len(delta_y)}")
                
    #             # implementing OLS regression on residuals to get half life
                hlx = n_past_spread
                hly = delta_y
                hlx = sm.add_constant(hlx)
                hl_result = sm.OLS(hly, hlx).fit()
                
    #             # extract the slope of the half life
                hl_slope = hl_result.params[1]
                
    #             # extract the half life
                hl = -(np.log(2))/hl_slope
                ivj.append(hl)
                masterList.append(ivj)
        print("\n")
                
    return masterList

# write it to an output file
def writeToFile(outputFile, masterListArr):
    with open(outputFile, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow("Asset 1, Asset 2, Hedge_Ratio, P_Value, Half_Life")
        for ivj in masterListArr:
            writer.writerow(ivj)



# allCloseData = getCloseData(tickerList[0])
# print(allCloseData)
# print(type(allCloseData['ZC=F']))
# masterListCreation(allCloseData, tickerList[0])

outputFileName = "project_1_Output.csv"

with open(outputFileName, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Asset y', 'Asset x', 'Hedge_Ratio', 'P_Value', 'Half_Life'])

for sector in tickerList:
    # print(ivjListCreation(getCloseData(sector), sector))
    print(f"-------------------------- {sector} --------------------------")
    allCloseData = getCloseData(sector)
    ivjData = ivjListCreation(allCloseData, sector)
    print(ivjData)

    writeToFile(outputFileName, ivjData)
    

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
