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
    rawData = yf.download(tickers=tickerListArr, period="2y", interval="1d", auto_adjust=True)
    closeData = rawData['Close']
    return closeData

# create the 2D arr of the data necessary
# tickerRow is the row of tickers for this asset class
# closeDataArr is the close data informatoin
def masterListCreation(closeDataArr, tickerRow):
    
    
    
    # CheckPoint 1: filter the data by dates *now unecessary*
    
    # Checking to see where the ticker values, dates, and tickers are
    # print("------------------------------DateTimeIndices------------------------------")
    # print(closeDataArr.index)
    # print("------------------------------Columns------------------------------")
    # print(closeDataArr.columns)
    # print("------------------------------Values------------------------------")
    # print(closeDataArr.values)
    myDataIndices = np.array(closeDataArr.index)
    myDataColumns = np.array(closeDataArr.columns)
    myDataVals = np.array(closeDataArr.values)
    
    myData = pd.DataFrame(data = myDataVals, index = myDataIndices, columns = myDataColumns)
    
    # testing whether checkpoint 2 works.
    # print("------------------------------My Data before length drop------------------------------")
    # print(myData.info(verbose=True))
    
    # Checking for consistency between my dataframe and the yf dataframe
    # print("------------------------------YF Data------------------------------")
    # print(closeDataArr)
    # print("------------------------------My Data before nan drop------------------------------")
    # print(myData)
    
    # print("------------------------------YF Data------------------------------")
    # print(closeDataArr.info(verbose=True))
    # print("------------------------------My Data B4 nan drop------------------------------")
    # print(myData.info(verbose=True))
    
# Testing to see whether the nan filter works (below)
    # sns = myData[closeDataArr.columns[3]]
    # i = 0
    # for val in sns:
    #     print(f"{sns.index[327]} | {i} | {val}")
    #     i += 1
    # print("nan line")
    # print("\n")
    # # print(type(sns.index[327]))
    # print(sns.index[327])
    # print("\n")
    # print(myData)
# Testing to see whether the nan filter works (above)
    
    
    # Checkpoint 1*: filter the data by Nan
    # This is to make sure I don't feed the math thingy nan data and
    # then it breaks because it got something it can't use (like nan).
    nanMask = set()
    
    # getting the index of the nan data within the columns of the various tickers.
    for ticker in tickerRow:
        nanIndex = 0
        for value in myData[ticker]:
            if (np.isnan(value) and len(nanMask) == 0):
                rowToDrop = myData[ticker].index[nanIndex]
                nanMask.add(rowToDrop)
                        
            nanIndex += 1
    
    # print(myData[nanMask])
    nanMaskList = [*nanMask]
    # print(nanMaskList[0].date())
    
    # extracting date information from the nanIndex obtained in the above for loop
    # and turning it into a string to input as a key into the data frame.
    print("\n")
    for data in nanMaskList:
        dataYear = "{:02d}".format(data.date().year)
        dataMonth = "{:02d}".format(data.date().month)
        dataDay = "{:02d}".format(data.date().day)
        stringifiedDate = f"{dataYear}-{dataMonth}-{dataDay}"
    
    # print the data before nan removal
        # print(stringifiedDate)
        # print("before nan removal")
        # print(myData)
        
        myData.drop([stringifiedDate], inplace = True)
        
    # print the data after nan removal
        # print("\n")
        # print("after")
        # print(myData)
        
    
# manually looking at the data to see whether the drop function actually worked (below)
    # print("\n")
    # print("------------------------------My Data after nan drop------------------------------")
    # print(myData)

    # for ticker in tickerRow:
    #     i = 0
    #     for val in myData[ticker]:
    #         print(f"{i} | {myData[ticker].index[i]} | {val}")
    #         i += 1
    #     print("\n")
    #     print("------------------------------My Data Lines------------------------------")
    #     print("\n")
    
    # print(myData.info(verbose=True)) #the most important line as it gives concise info
# manually looking at the data to see whether the drop function actually worked (above)
        

    # Checkpoint 2*: filter the data by number of data points
    # you will drop the column that doesn't have enough data points!!!!
    # lenMaskIndices
    for ticker in tickerRow:
        if len(myData[ticker]) < 300:
            myData.drop(columns=[ticker])
     
# Testing whether checkpiont 2 works       
    # print("------------------------------My Data post length drop------------------------------")
    # print(myData.info(verbose=True))
    
   
    master_list = []

    for i in range(0, len(tickerRow)):
        for j in range(i+1,len(tickerRow)-1):
            

    #     # smol list
            ivj = []
            ivj.append(tickerRow[i])
            ivj.append(tickerRow[j])
            
            
    #     # hedge ratio
            x = np.log(closeDataArr[tickerRow[i]].tolist())
            y = np.log(closeDataArr[tickerRow[j]].tolist())
            x = sm.add_constant(x)
            result = sm.OLS(y, x).fit()
            hedge_ratio = result.params[1]
            ivj.append(hedge_ratio)
        
    #     # residuals
            residuals = result.resid
            
    #     # p-value
            ADF_test = adfuller(residuals)
            p_val = ADF_test[1]
            
    #     # conditional logic
            if p_val < 0.05:
            
    #         # do all this
            
                ivj.append(p_val)
            
    #         # calculating half life
            
                # delta_y = todays spread - yesterdays spread
                delta_y = np.diff(residuals)

    #             # yesterdays spread
                past_spread = np.roll(residuals, 1)
                mask = ~past_spread[0]
                n_past_spread = past_spread[mask]
                
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
                master_list.append(ivj)
                
    return master_list

# write it to an output file
def writeToFile(outputFile, masterListArr):
    with open(outputFile, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow("Asset 1, Asset 2, Hedge_Ratio, P_Value, Half_Life")
        for ivj in masterListArr:
            writer.writerow(ivj)



# allCloseData = getCloseData(zipperTest)
# print(allCloseData)
# print(type(allCloseData['ZC=F']))
# masterListCreation(getCloseData(tickerList[3]), tickerList[3])

for sector in tickerList:
    masterListCreation(getCloseData(sector), sector)
    print(masterListCreation(getCloseData(sector), sector))
#     allCloseData = getCloseData(sector)
#     masterData = masterListCreation(allCloseData, sector)
#     writeToFile("project_1_Output.csv", masterData)
    



# determine which 10 sectors to go in
# determine which 5 futures of those sectors to go in
# get the tickers
# create the 10 lists of 5 futures
# run all 3 functions on each of the 10 lists
# just make a 2d list with all the futures.
# for sector in market:
    # run function 1
    # run function 2
    # run function 3
    
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
