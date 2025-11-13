import re
import requests
import traceback
import urllib.parse
import yfinance as yf

from bs4 import BeautifulSoup


def parse_stock_command(text: str):
    """
    If text starts with '#', extract the symbol and return it with market type.
    For Taiwan stocks: #2330, #00930A -> ('2330', 'TW'), ('00930A', 'TW')
    For US stocks: #AAPL -> ('AAPL', 'US')
    Otherwise, return None.
    """
    if text == "#大盤":
        return ("^TWII", "TW")
    
    match = re.match(r'^#(.+)', text.strip())
    if match:
        symbol = match.group(1)
        symbol = re.sub(r"\s+", "", symbol)   # remove all whitespace via regex
        # Check if it's a Taiwan stock or US stock
        # Taiwan stocks: start with digits (may contain letters at the end)
        # US stocks: start with letters
        if symbol[0].isdigit():
            return (symbol, 'TW')
        elif bool(re.search(r'[\u4e00-\u9fff]', symbol)):
            symbol = get_tw_stock_symbol_from_company_name(symbol)
            if symbol:
                return (symbol, 'TW')
        elif bool(re.search(r'^[A-Za-z0-9]+', symbol)):
            return (symbol.upper(), 'US')

    return None


def get_tw_stock_price(symbol: str):
    """
    Get real-time stock price for a Taiwan stock symbol using yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        yahoo_symbol = symbol if symbol == "^TWII" else f"{symbol}.TW"
        ticker = yf.Ticker(yahoo_symbol)
        
        # Get current price info
        info = ticker.info
        stock_name = get_tw_stock_name(symbol, "TW")

        if not info or info.get('regularMarketPrice') is None :
            # fallback to TWO market
            yahoo_symbol = f"{symbol}.TWO"
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            stock_name = get_tw_stock_name(symbol, "TWO")

        history = ticker.history(period="1d")

        if not history.empty and info:
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
        print(f"Error fetching stock price with yfinance: {e}")
        return _fallback_stock_price(symbol)
    return None


def get_us_stock_price(symbol: str):
    """
    Get real-time stock price for a US stock symbol using yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current price info
        info = ticker.info
        history = ticker.history(period="1d")

        if not history.empty and info:
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            previous_close = info.get('regularMarketPreviousClose')

            return {
                'symbol': symbol,
                'name': info.get('shortName', info.get('longName', f'Stock {symbol}')),
                'price': round(current_price, 2),
                'previous_price': round(previous_close, 2),
                'currency': info.get('currency', 'USD'),
                'time': None,
                'upsOrDowns': get_ups_or_downs(current_price, previous_close)
            }
    except Exception as e:
        print(f"Error fetching US stock price with yfinance: {e}")
    return None


def get_ups_or_downs(current_price, previous_close):
    """
    Determine if the stock price is up, down, or unchanged.
    Returns 1 for up, -1 for down, 0 for unchanged.
    """
    if current_price > previous_close:
        return 1
    elif current_price < previous_close:
        return -1
    else:
        return 0


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
        print(f"Error with fallback method: {e}")
    
    return None


def get_tw_stock_name(symbol: str, markey_type: str):
    if symbol == "^TWII":
        return "台灣加權指數"

    if markey_type == "TW":
        return get_tw_stock_name_from_twse(symbol)
    elif markey_type == "TWO":
        return get_tw_stock_name_from_tpex(symbol)

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
        print(f"Error fetching Taiwan stock name for {symbol} from tpse: {e}")
    
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
        print(f"Error fetching Taiwan stock name for {symbol} from tpex: {e}")
        traceback.print_exc()

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
                print(f"Taiwan stock symbol for name {company_name} not found from twse")
                return None
            
    except Exception as e:
        print(f"Error fetching Taiwan stock symbol for name {company_name} from twse: {e}")
        traceback.print_exc()

    return None


def search_stock_by_name(company_name: str):
    """
    Search Taiwan stock symbol by company name using TWSE REST API.
    Returns a list of matching stocks or empty list if not found.
    """
    try:
        #  TWSE API endpoint for searching companies
        url = "https://www.twse.com.tw/rwd/zh/company/codeQuery"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Get all company data first
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            results = []
            if 'data' in data and data['data']:
                for item in data['data']:
                    if len(item) >= 2:
                        symbol = item[0]
                        name = item[1]
                        # Check if company name contains the search term
                        if company_name in name:
                            results.append({
                                'symbol': symbol,
                                'name': name
                            })
            
            return results

        # Alternative: Try TWSE listed companies endpoint
        alt_url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL"
        alt_params = {
            'response': 'json'
        }

        resp = requests.get(alt_url, params=alt_params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            results = []
            if data.get('stat') == 'OK' and 'data' in data:
                for stock_data in data['data']:
                    if len(stock_data) >= 2:
                        symbol = stock_data[0]
                        name = stock_data[1]
                        # Check if company name contains the search term
                        if company_name in name:
                            results.append({
                                'symbol': symbol,
                                'name': name
                            })
            
            return results
    
    except Exception as e:
        print(f"Error searching stock by name '{company_name}': {e}")
        traceback.print_exc()
    
    return []


def search_tpex_stock_by_name(company_name: str):
    """
    Search Taiwan OTC stock symbol by company name using TPEx REST API.
    Returns a list of matching stocks or empty list if not found.
    """
    try:
        # TPEx API endpoint for OTC companies
        url = "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php"
        params = {
            'l': 'zh-tw',
            'se': 'AL'  # All listed
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()

            results = []
            if 'aaData' in data:
                for item in data['aaData']:
                    if len(item) >= 2:
                        symbol = item[0]
                        name = item[1]
                        # Check if company name contains the search term
                        if company_name in name:
                            results.append({
                                'symbol': symbol,
                                'name': name,
                                'market': 'TPEx'
                            })
            
            return results
    
    except Exception as e:
        print(f"Error searching TPEx stock by name '{company_name}': {e}")
        traceback.print_exc()
    
    return []


def search_all_taiwan_stocks_by_name(company_name: str):
    """
    Search all Taiwan stocks (both TWSE and TPEx) by company name.
    Returns a combined list of matching stocks.
    """
    results = []
    
    # Search TWSE (上市) stocks
    twse_results = search_stock_by_name(company_name)
    for stock in twse_results:
        stock['market'] = 'TWSE'
        results.append(stock)

    # Search TPEx (上櫃) stocks
    tpex_results = search_tpex_stock_by_name(company_name)
    results.extend(tpex_results)
    
    return results


def get_stock_info(text: str):
    parsed_result = parse_stock_command(text)
    if parsed_result:
        symbol, market = parsed_result
        
        if market == 'TW':
            price_info = get_tw_stock_price(symbol)
        elif market == 'US':
            price_info = get_us_stock_price(symbol)
        else:
            price_info = None
        
        return price_info
    return None
