import pandas as pd  
from datetime import datetime, timedelta  
from alpaca.data.historical import StockHistoricalDataClient  
from alpaca.data.requests import StockBarsRequest  
from alpaca.data.timeframe import TimeFrame  
from config import API_KEY, API_SECRET  
import strategies.trading_strategies_v2 as trading_strategies_v2
import helper_files.client_helper
from pymongo import MongoClient
from helper_files.client_helper import get_ndaq_tickers
from config import MONGO_DB_USER, MONGO_DB_PASS

mongo_url = f"mongodb+srv://{MONGO_DB_USER}:{MONGO_DB_PASS}@cluster0.0qoxq.mongodb.net"

def get_historical_data(ticker, client, days=100):  
   """  
   Fetch historical bar data for a given stock ticker.  
    
   :param ticker: The stock ticker symbol.  
   :param client: An instance of StockHistoricalDataClient.  
   :param days: Number of days of historical data to fetch.  
   :return: DataFrame with historical stock bar data. test all data for all tickers - try to follow trading client specification  
   """  
   start_time = datetime.now() - timedelta(days=days)  
   request_params = StockBarsRequest(  
      symbol_or_symbols=ticker,  
      timeframe=TimeFrame.Day,  
      start=start_time  
   )  
    
   bars = client.get_stock_bars(request_params)  
   data = bars.df  
   return data  

def test_strategies():
   
   # Initialize the StockHistoricalDataClient  
   client = StockHistoricalDataClient(API_KEY, API_SECRET)  
   mongo_client = MongoClient() 
   tickers = get_ndaq_tickers(mongo_url)
   tickers = tickers + ['DBRG', 'WTFC', 'AESI', 'MDB', 'SNPS', 'CRUS', 'RRR', 'CI', 'OSK', 'AZZ']
   # Define test parameters  
   for ticker in tickers:  
    account_cash = 10000  
    portfolio_qty = 100
    total_portfolio_value = 100000  
    
    historical_data = get_historical_data(ticker, client) 
    current_price = historical_data['close'].iloc[-1]
    # Test each strategy  
    strategies = [  
        trading_strategies_v2.conners_rsi_strategy
        
    ] 
    
    for strategy in strategies:  
        decision, quantity, ticker = strategy(  
            ticker,  
            current_price,  
            historical_data,  
            account_cash,  
            portfolio_qty,  
            total_portfolio_value  
        )  
        if decision != "hold":
         print(f"{strategy.__name__}:")  
         print(f"  Decision: {decision}")  
         print(f"  Ticker: {ticker}")  
         print(f"  Quantity: {quantity}")  
         print("__________________________________________________")  
   mongo_client.close()
def test_helper():
   print(helper_files.client_helper.get_latest_price("AAPL"))
if __name__ == "__main__":  
   test_strategies()