import logging
import requests
import urllib.parse
import yfinance as yf

from bs4 import BeautifulSoup
from quote.common import get_ups_or_downs

logger = logging.getLogger(__name__)


def get_tw_stock_price(symbol: str) -> dict | None:
    """
    Get real-time stock price for a Taiwan stock symbol using yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        market_type = "TW"
        yahoo_symbol = symbol if symbol == "^TWII" else f"{symbol}.{market_type}"
        ticker = yf.Ticker(yahoo_symbol)
        
        # Get current price info
        info = ticker.info

        if not info or info.get('regularMarketPrice') is None :
            # fallback to TWO market
            market_type = "TWO"
            yahoo_symbol = f"{symbol}.{market_type}"
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info

        history = ticker.history(period="1d")

        if not history.empty and info:
            stock_name = get_tw_stock_name(symbol, market_type)
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            previous_close = info.get('regularMarketPreviousClose')

            if not stock_name:
                stock_name = info.get('shortName', info.get('longName', f'Stock {symbol}'))  # fallback to yahoo's result

            return {
                'symbol': symbol,
                'name': stock_name,
                'price': round(current_price, 2),
                'previous_price': round(previous_close, 2),
                'currency': info.get('currency', 'TWD'),
                'time': None,
                'upsOrDowns': get_ups_or_downs(current_price, previous_close)
            }
    except ImportError:
        # Fallback to simple web scraping if yfinance not available
        return _fallback_stock_price(symbol)
    except Exception as e:
        logger.error(f"Error fetching stock price with yfinance: {e}")
        logger.exception(e)
        return _fallback_stock_price(symbol)

    return None


def _fallback_stock_price(symbol: str):
    """
    Fallback method using Taiwan Stock Exchange API or web scraping.
    """
    try:
        # Try Taiwan Stock Exchange API
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&stockNo={symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('stat') == 'OK' and data.get('data'):
                # Get the most recent data
                latest_data = data['data'][-1]
                price = float(latest_data[1])  # Close price
                
                return {
                    'symbol': symbol,
                    'name': f'Stock {symbol}',
                    'price': price,
                    'currency': 'TWD',
                    'time': None
                }
    except Exception as e:
        logger.error(f"Error with fallback method: {e}")
        logger.exception(e)
    
    return None


def get_tw_stock_name(symbol: str, markey_type: str) -> str | None:
    match markey_type:
        case "TW":
            if symbol == "^TWII":
                return "台灣加權指數"
            return get_tw_stock_name_from_twse(symbol)
        case "TWO":
            return get_tw_stock_name_from_tpex(symbol)
        case _:
            return None


def get_tw_stock_name_from_twse(symbol: str):
    """
    Get Taiwan stock's Chinese name using TWSE REST API.
    Returns the Chinese name of the stock or None if not found.
    """
    try:
        # TWSE API endpoint for stock basic information
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        params = {
            'response': 'json',
            'date': '',  # Current month
            'stockNo': symbol
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            # Check if the response contains stock data
            if data.get('stat') == 'OK':
                # The stock name is usually in the title field
                title = data.get('title', '')
                if title:
                    # Extract stock name from title, Format: "114年10月 2884 玉山金           各日成交資訊"
                    
                    parts = title.split()
                    if len(parts) >= 4:
                        stock_name = parts[-2]
                        return stock_name
        
        # Alternative API endpoint for company basic info
        alt_url = "https://www.twse.com.tw/rwd/zh/company/codeQuery"
        alt_params = {
            'STK_NO': symbol
        }
        
        resp = requests.get(alt_url, params=alt_params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            # Extract company name from response
            if 'data' in data and data['data']:
                for item in data['data']:
                    if len(item) >= 2 and item[0] == symbol:
                        return item[1]  # Company name is usually in the second column
        
        # Try another endpoint for listed companies
        list_url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL"
        list_params = {
            'response': 'json'
        }
        
        resp = requests.get(list_url, params=list_params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            if data.get('stat') == 'OK' and 'data' in data:
                for stock_data in data['data']:
                    if len(stock_data) >= 2 and stock_data[0] == symbol:
                        return stock_data[1]  # Stock name
        
    except Exception as e:
        logger.error(f"Error fetching Taiwan stock name for {symbol} from tpse: {e}")
        logger.exception(e)

    return None


def get_tw_stock_name_from_tpex(symbol: str):
    if len(symbol) > 4:
        url = f"https://info.tpex.org.tw/api/etfProduct?query={symbol}"
    else:
        url = f"https://info.tpex.org.tw/api/stkInfo?query={symbol}"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if 'info' in data:
                return data['info'].get('shortName', None)  # for stock

            return data.get('shortName', None)  # for ETF
    except Exception as e:
        logger.error(f"Error fetching Taiwan stock name for {symbol} from tpex: {e}")
        logger.exception(e)

    return None


def get_tw_stock_symbol_from_company_name(company_name: str):
    url = "https://mopsov.twse.com.tw/mops/web/ajax_autoComplete"
    encoded_company_name = urllib.parse.quote(company_name)
    payload = f"encodeURIComponent=1&step=1&firstin=ture&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&inpuType=co_id&TYPEK=all&co_id={encoded_company_name}&sstep=1"
    
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code == 200:
            # Parse HTML
            soup = BeautifulSoup(resp.content, "html.parser")

            # Find the element by id
            element = soup.find(id="autoDiv-1")

            # Extract its value
            if element and element.has_attr("value"):
                return element["value"]
            else:
                logger.warning(f"Taiwan stock symbol for name {company_name} not found from twse")
                return None
            
    except Exception as e:
        logger.error(f"Error fetching Taiwan stock symbol for name {company_name} from twse: {e}")
        logger.exception(e)

    return None
