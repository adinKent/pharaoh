import logging
import requests
import urllib.parse
import yfinance as yf

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from quote.output import format_price_output

logger = logging.getLogger(__name__)


def get_tw_stock_price(symbol: str) -> dict | None:
    """
    Get real-time stock price for a Taiwan stock symbol using yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        market_type = "TW"
        yahoo_symbol = f"{symbol}.{market_type}"
        ticker = yf.Ticker(yahoo_symbol)
        
        # Get current price info
        info = ticker.info

        if not info or info.get('regularMarketPrice') is None :
            # fallback to TWO market
            market_type = "TWO"
            yahoo_symbol = f"{symbol}.{market_type}"
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info

        history = ticker.history(period="2d")

        if not history.empty and info:
            result = format_price_output(symbol, info)
            result['name'] = get_tw_stock_name(symbol, market_type) or result['name']

            return result
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


def format_twse_buy_and_sell_result(bug_sell_data: dict) -> str | None:
    """
    Format TWSE fund result JSON to a pretty text.
    """
    if not bug_sell_data or bug_sell_data.get('stat') != 'OK':
        return None

    fields = bug_sell_data.get('fields', [])
    data = bug_sell_data.get('data', [])
    title = bug_sell_data.get('title', '')
    notes = bug_sell_data.get('notes', [])
    hints = bug_sell_data.get('hints', '')

    # Convert numeric columns (except the first column) to units of 100 million
    converted_data = []
    for row in data:
        new_row = [row[0]]
        for cell in row[1:]:
            try:
                num = float(cell.replace(',', ''))
                new_cell = f"{num / 100_000_000:.2f}"
            except Exception:
                new_cell = cell
            new_row.append(new_cell)
        converted_data.append(new_row)

    lines = []
    if title:
        lines += [title, '']

    foreign_row = converted_data[3]
    for i in range(1, len(foreign_row)):
        lines.append(f"外資{fields[i]}:{foreign_row[i].rjust(8)}")

    lines.append("")  # separator

    for row in [converted_data[2], converted_data[0], converted_data[1], converted_data[5]]:  # 投信、自營商(自行買賣)、自營商(避險)、合計
        for i in range(1, len(row)):
            lines.append(f"{row[0]}{fields[i]}:{row[i].rjust(8)}")
        lines.append("")

    lines.append('單位：億元')

    return '\n'.join(lines)


def previous_working_day(date):
    # Go backwards until it's Monday–Friday
    while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        date -= timedelta(days=1)
    return date


def get_effective_date():
    now = datetime.now()
    cutoff = now.replace(hour=15, minute=0, second=0, microsecond=0)
    
    if now >= cutoff:
        # After 3PM → today (if weekday), else previous working day
        if now.weekday() < 5:
            return now.date()
        else:
            return previous_working_day(now.date() - timedelta(days=1))
    else:
        # Before 3PM → previous working day
        return previous_working_day(now.date() - timedelta(days=1))


def get_twse_buy_sell_today_result() -> str | None:
    """
    Fetch today's buy sell result from TWSE using the provided URL format.
    Format the JSON response to a table like str, or None on failure.
    """
    today = get_effective_date().strftime('%Y%m%d')
    url = (
        f"https://www.twse.com.tw/rwd/zh/fund/BFI82U?"
        f"type=day&dayDate={today}&weekDate={today}&monthDate={today}&response=json&_={int(datetime.now().timestamp() * 1000)}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return format_twse_buy_and_sell_result(resp.json())
    except Exception as e:
        logger.error(f"Error fetching TWSE fund result: {e}")
        logger.exception(e)
        return None
