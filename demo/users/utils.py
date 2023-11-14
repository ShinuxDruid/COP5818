import yfinance as yf
from datetime import datetime, timedelta
import requests

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    return data.to_dict()

def get_stock_data_for_last_month(symbol):
    # Get stock data for the last month using yfinance
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        stock_data = yf.download(symbol, start=start_date, end=end_date)
        return stock_data
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

def get_data(from_symbol, to_symbol, API_KEY):
    r = requests.get('https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=' + from_symbol + '&to_symbol=' + to_symbol + '&apikey=' + API_KEY)

    dataIntraday = r.json()

    return dataIntraday['Time Series FX (Daily)']
