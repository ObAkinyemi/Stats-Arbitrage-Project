import yfinance as yf
import pandas as pd

tickerList = ['AAPL', 'MSFT', 'GOOG', 'NVDA', 'AMD', 'INTC', 'TSM', 'QCOM', 'TXN', 'AMAT']

# auto_adjust = true gives me all the adjusted close data (I think)
rawData = yf.download(tickers=tickerList, period="2y", interval="1d", auto_adjust=True)

# print(DownloadedData)
print(type(rawData))
# Close, Open, 
print(rawData['Close'])