import yfinance as yf
import pandas as pd

tickerList = ['ES=F', 'YM=F', 'CL=F', 'NG=F', 'GC=F', 'HG=F', '6E=F', '6J=F', 'ZB=F', 'ZN=F']

# auto_adjust = true gives me all the adjusted close data (I think)
rawData = yf.download(tickers=tickerList, period="2y", interval="1d", auto_adjust=True)
closeData = rawData['Close']
# print(DownloadedData)
# print(type(rawData))
# Close, Open, 
# print(rawData['Close'])

#loop through i (the tickers) done
# loop through j (the price data)
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
for i in range(i, len(tickerList)):
    # print("Ticker i data: " + str(i) + str(closeData[tickerList[i]]))
    for j in range(i+1,len(tickerList)-1):
        # print("J: " + str(j) + "and I: " + str(i))
        print("Ticker " + tickerList[i] + " vs Ticker" + tickerList[j])
        
# Now