import yfinance as yf
import pandas as pd
import csv

tickerList = ['ES=F', 'YM=F', 'CL=F', 'NG=F', 'GC=F', 'HG=F', '6E=F', '6J=F', 'ZB=F', 'ZN=F']
# auto_adjust = true gives me all the adjusted close data (I think)
rawData = yf.download(tickers=tickerList, period="2y", interval="1d", auto_adjust=True)
closeData = rawData['Close']
# print(DownloadedData)
print(rawData['Close']['ES=F'].keys())
# Close, Open, 
# print(rawData['Close'])

#loop through i (the tickers) done
# loop through j (the the comparative tickers)
# loop through k (the price data using iloc)
# Create a 2D array with the ticker data with the following structure
    # [
        # [ticker 1 data, ticker 2 data], [ticker 1 data, ticker 2 data]
        # [ticker 1 data, ticker 3 data], [ticker 1 data, ticker 3 data]
        # .
        # .
        # .
        # [ticker 8 data, ticker 9 data]
# j != i
# create a dictionary with the following structure for all tickers.
# create all possible sets of 2
# ticker vs ticker:
    # [ticker1 data, ticker 2 data]
    
i = 0
j = 0

# this is the logic for the comparison
# for i in range(i, len(tickerList)):
#     # print("Ticker i data: " + str(i) + str(closeData[tickerList[i]]))
    
#     for j in range(i+1,len(tickerList)-1):
#         # Now loop through the price data using the length of the
#         # rawData['Close']['ES=F'].iloc[k] and pit the tickers against each other
       
#         print(f"ticker i: {tickerList[i]} vs ticker j: {tickerList[j]}")
#         with open('test.csv', 'a', newline='') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow([tickerList[i], tickerList[j]])
        
#             for k in range(0, len(rawData['Close'][tickerList[i]])-495):
#                 print(f"{rawData['Close'][tickerList[i]].iloc[k]} vs {rawData['Close'][tickerList[j]].iloc[k]}")
#                 writer.writerow([rawData['Close'][tickerList[i]].iloc[k], rawData['Close'][tickerList[j]].iloc[k]])
