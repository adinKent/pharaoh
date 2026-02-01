import urllib.parse
import logging
import csv
import re
import io
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from io import StringIO
from pathlib import Path
import time

import requests
import yfinance as yf
from bs4 import BeautifulSoup
from pymongo import UpdateOne
import pandas as pd
import matplotlib.font_manager as fm
import mplfinance as mpf

from quote.output import (
	format_price_output,
    get_info_for_day_candle_picture
)
from quote.fugle import (
    quote_stock,
    quote_stock_ticker,
    quote_stock_candles
)
from utils.mongo_helper import get_mongo_client
from utils.aws_helper import put_image

HERE = Path(__file__).resolve().parent.parent
FONT_PATH = HERE / "assets" / "fonts" / "NotoSansTC-Regular.ttf"

logger = logging.getLogger(__name__)

def get_tw_stock_price(symbol: str, period: str | None = None, yf_symbol: str | None = None) -> dict | None:
    """
    Get real-time stock price for a Taiwan stock symbol using fugle and yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        stock_info = quote_stock(symbol)
        if stock_info:

            current_price = stock_info.get('lastPrice', stock_info.get('closePrice'))
            previous_close = stock_info.get('previousClose')

            yf_stock_info = {
                "exchange": stock_info.get("exchange", "TWSE"),
                # normalize fields to yahoo finance format
                "symbol": symbol,
                "shortName": stock_info.get("name", symbol),
                "currentPrice": current_price,
                "regularMarketPrice": current_price, 
                "regularMarketPreviousClose": previous_close,
                "currency": "TWD",
            }

            history = dict()
            if period:
                exchange = stock_info.get("exchange", "TWSE")
                yahoo_symbol = yf_symbol
                if not yahoo_symbol:
                    market_type = "TW" if exchange == "TWSE" else "TWO"
                    yahoo_symbol = f"{symbol}.{market_type}"
                ticker = yf.Ticker(yahoo_symbol)
                history = ticker.history(period=period)

            return format_price_output(symbol, yf_stock_info, history)
    except ImportError:
        # Fallback to simple web scraping if yfinance not available
        return _fallback_stock_price(symbol)
    except Exception as e:
        logger.error("Error fetching stock price with yfinance: %s", e)
        logger.exception(e)
        return _fallback_stock_price(symbol)

    return None

def get_tw_index_price(symbol: str, period: str | None = None) -> dict | None:
    """
    Get real-time index price for a Taiwan index symbol using fugle and yfinance library.
    Returns a dict with price info or None if not found.
    """
    yahoo_symbol = None
    if symbol == "IX0001":
        yahoo_symbol = "^TWII"
    elif symbol == "IX0043":
        yahoo_symbol = "IX0043.TWO"

    return get_tw_stock_price(symbol, period, yahoo_symbol)


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
        logger.error("Error with fallback method: %s", e)
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
        logger.error("Error fetching Taiwan stock name for %s from tpse: %s", symbol, e)
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
                logger.warning("Taiwan stock symbol for name %s not found from twse", company_name)
                return None

    except Exception as e:
        logger.error("Error fetching Taiwan stock symbol for name %s from twse: %s", company_name, e)
        logger.exception(e)

    return None


def format_total_net_diff(field_name, amount):
    result = amount
    if "差額" in field_name:
        amount_number = float(amount)
        if amount_number > 0:
            result = f'+{amount_number}'
    
    return result

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
        field_name = fields[i]
        amount = format_total_net_diff(field_name, foreign_row[i])
        lines.append(f"外資{fields[i]}:{amount.rjust(8)}")

    lines.append("")  # separator

    for row in [converted_data[2], converted_data[0], converted_data[1], converted_data[5]]:  # 投信、自營商(自行買賣)、自營商(避險)、合計
        for i in range(1, len(row)):
            field_name = fields[i]
            amount = format_total_net_diff(field_name, row[i])
            lines.append(f"{row[0]}{field_name}:{amount.rjust(8)}")
        lines.append("")

    lines.append('單位：億元')

    return '\n'.join(lines)


def previous_working_day(date):
    # Go backwards until it's Monday–Friday
    while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        date -= timedelta(days=1)
    return date


def get_effective_date():
    now = datetime.now(ZoneInfo("Asia/Taipei"))
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


def get_institues_buy_sell_today_result() -> str | None:
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
        logger.error("Error fetching TWSE fund result: %s", e)
        logger.exception(e)
        return None


def get_twse_buy_sell_today_result() -> list[dict] | None:
    """
    Downloads and parses the foreign and other investor trade summary from TWSE.

    The data is fetched from a CSV endpoint for a specific date.
    URL: https://www.twse.com.tw/rwd/zh/fund/T86?date=YYYYMMDD&selectType=ALL&response=csv

    Returns:
        A list of dictionaries, where each dictionary represents a stock's
        trade data, or None if fetching or parsing fails.
    """
    today = get_effective_date().strftime('%Y%m%d')
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={today}&selectType=ALL&response=csv"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        # The response text contains informational headers and footers.
        # We need to find where the actual CSV starts.
        lines = resp.text.splitlines()
        csv_content = []
        data_started = False
        for line in lines:
            if '證券代號' in line:
                data_started = True
            if data_started and line.strip():
                if '說明' in line:  # data end
                    break
                else:
                    csv_content.append(line)

        reader = csv.DictReader(StringIO('\n'.join(csv_content)))
        return [row for row in reader]
    except Exception as e:
        logger.error("Error fetching or parsing TWSE bug and sell CSV for date %s: %s", url, e)
        logger.exception(e)
        return None


def get_tpex_buy_sell_today_result() -> list[dict] | None:
    """
    Downloads and parses the foreign and other investor trade summary from TPEX.

    The data is fetched from a CSV endpoint for a specific date.
    URL: https://www.tpex.org.tw/www/zh-tw/insti/dailyTrade?type=Daily&sect=AL&date=YYYY-MM--DD&id=&response=csv

    Returns:
        A list of dictionaries, where each dictionary represents a stock's
        trade data, or None if fetching or parsing fails.
    """
    today = urllib.parse.quote(get_effective_date().strftime('%Y-%m-%d'))
    url = f"https://www.tpex.org.tw/www/zh-tw/insti/dailyTrade?type=Daily&sect=AL&date={today}id=&response=csv"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        # The response text contains informational headers and footers.
        lines = resp.text.splitlines()
        csv_content = []
        data_started = False
        for line in lines:
            if '代號' in line and '名稱' in line:
                data_started = True
            if data_started and line.strip():
                if re.search(r"共\d+筆", line):  # data end
                    break
                else:
                    csv_content.append(line)

        reader = csv.DictReader(StringIO('\n'.join(csv_content)))
        return [row for row in reader]
    except Exception as e:
        logger.error("Error fetching or parsing TWSE bug and sell CSV for date %s: %s", url, e)
        logger.exception(e)
        return None


def sync_all_buy_sell_today_result_to_db():
    matched_count = 0
    upserted_count = 0

    try:
        with get_mongo_client() as client:
            try:
                db = client['TaiwanMarket']
                collection = db['buyAndSell']
            except Exception as e:
                logger.error("Failed to connect to MongoDB: %s", e)
                logger.exception(e)
                return (0, 0)

            trade_date = get_effective_date().strftime('%Y-%m-%d')
            db_bulk_operations = []
            twse_result = get_twse_buy_sell_today_result()
            if twse_result:
                for row in twse_result:
                    doc = normalize_twse_stock_buy_sell_to_db_format(row)
                    doc['date'] = trade_date
                    doc['market'] = 'TWSE'
                    db_bulk_operations.append(UpdateOne(
                        {'_id': doc['symbol']},
                        {'$set': doc},
                        upsert=True
                    ))

            tpex_result = get_tpex_buy_sell_today_result()
            if tpex_result:
                for row in tpex_result:
                    doc = normalize_tpex_stock_buy_sell_to_db_format(row)
                    doc['date'] = trade_date
                    doc['market'] = 'TPEX'
                    db_bulk_operations.append(UpdateOne(
                        {'_id': doc['symbol']},
                        {'$set': doc},
                        upsert=True
                    ))


            if len(db_bulk_operations) > 0:
                result = collection.bulk_write(db_bulk_operations)
                matched_count = result.matched_count
                upserted_count = result.upserted_count
                logger.info("Synced to DB. Matched: %s, Upserted: %s", result.matched_count, result.upserted_count)
    except Exception as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        logger.exception(e)

    return (matched_count, upserted_count)


def normalize_twse_stock_buy_sell_to_db_format(row:dict) -> dict:
    '''
    0: 證券代號
    1: 證券名稱
    2: 外陸資買進股數(不含外資自營商)
    3: 外陸資賣出股數(不含外資自營商)
    4: 外陸資買賣超股數(不含外資自營商)
    5: 外資自營商買進股數
    6: 外資自營商賣出股數
    7: 外資自營商買賣超股數
    8: 投信買進股數
    9: 投信賣出股數
    10:投信買賣超股數
    11:自營商買賣超股數
    12:自營商買進股數(自行買賣)
    13:自營商賣出股數(自行買賣)
    14:自營商買賣超股數(自行買賣)
    15:自營商買進股數(避險)
    16:自營商賣出股數(避險)
    17:自營商買賣超股數(避險)
    18:三大法人買賣超股數
    '''

    return {
        'symbol': re.sub(r'[="\s]', '', row['證券代號']),
        'name': re.sub(r'[="\s]', '', row['證券名稱']),
        'foreignBuy': row['外陸資買進股數(不含外資自營商)'],
        'foreignSell': row['外陸資賣出股數(不含外資自營商)'],
        'foreignNet': row['外陸資買賣超股數(不含外資自營商)'],
        'foreignDealerBuy': row['外資自營商買進股數'],
        'foreignDealerSell': row['外資自營商賣出股數'],
        'foreignDealerNet': row['外資自營商買賣超股數'],
        'investTrustBuy': row['投信買進股數'],
        'investTrustSell': row['投信賣出股數'],
        'investTrustNet': row['投信買賣超股數'],
        'dealerTotalNet': row['自營商買賣超股數'],
        'dealerBuy': row['自營商買進股數(自行買賣)'],
        'dealerSell': row['自營商賣出股數(自行買賣)'],
        'dealerNet': row['自營商買賣超股數(自行買賣)'],
        'dealerHedgeBuy': row['自營商買進股數(避險)'],
        'dealerHedgeSell': row['自營商賣出股數(避險)'],
        'dealerHedgeNet': row['自營商買賣超股數(避險)'],
        'totalNet': row['三大法人買賣超股數']
    }


def normalize_tpex_stock_buy_sell_to_db_format(row:dict) -> dict:
    '''
    0: 代號
    1: 名稱
    2: 外資及陸資(不含外資自營商)-買進股數
    3: 外資及陸資(不含外資自營商)-賣出股數
    4: 外資及陸資(不含外資自營商)-買賣超股數
    5: 外資自營商-買進股數
    6: 外資自營商-賣出股數
    7: 外資自營商-買賣超股數
    8: 外資及陸資-買進股數
    9: 外資及陸資-賣出股數
    10: 外資及陸資-買賣超股數
    11: 投信-買進股數
    12: 投信-賣出股數
    13: 投信-買賣超股數
    14: 自營商(自行買賣)-買進股數
    15: 自營商(自行買賣)-賣出股數
    16: 自營商(自行買賣)-買賣超股數
    17: 自營商(避險)-買進股數
    18: 自營商(避險)-賣出股數
    19: 自營商(避險)-買賣超股數
    20: 自營商-買進股數
    21: 自營商-賣出股數
    22: 自營商-買賣超股數
    23: 三大法人買賣超股數合計
    '''

    return {
        'symbol': re.sub(r'[="\s]', '', row['代號']),
        'name': re.sub(r'[="\s]', '', row['名稱']),
        'foreignBuy': row['外資及陸資(不含外資自營商)-買進股數'],
        'foreignSell': row['外資及陸資(不含外資自營商)-賣出股數'],
        'foreignNet': row['外資及陸資(不含外資自營商)-買賣超股數'],
        'foreignDealerBuy': row['外資自營商-買進股數'],
        'foreignDealerSell': row['外資自營商-賣出股數'],
        'foreignDealerNet': row['外資自營商-買賣超股數'],
        'foreignTotalBuy': row['外資及陸資-買進股數'],
        'foreignTotalSell': row['外資及陸資-賣出股數'],
        'foreignTotalNet': row['外資及陸資-買賣超股數'],
        'investTrustBuy': row['投信-買進股數'],
        'investTrustSell': row['投信-賣出股數'],
        'investTrustNet': row['投信-買賣超股數'],
        'dealerBuy': row['自營商(自行買賣)-買進股數'],
        'dealerSell': row['自營商(自行買賣)-賣出股數'],
        'dealerNet': row['自營商(自行買賣)-買賣超股數'],
        'dealerHedgeBuy': row['自營商(避險)-買進股數'],
        'dealerHedgeSell': row['自營商(避險)-賣出股數'],
        'dealerHedgeNet': row['自營商(避險)-買賣超股數'],
        'dealerTotalBuy': row['自營商-買進股數'],
        'dealerTotalSell': row['自營商-賣出股數'],
        'dealerTotalNet': row['自營商-買賣超股數'],
        'totalNet': row['三大法人買賣超股數合計']
    }


def get_symbol_buy_sell_today_result(symbol:str) -> dict | None:
    try:
        with get_mongo_client() as client:
            db = client['TaiwanMarket']
            collection = db['buyAndSell']
            return collection.find_one({'_id': symbol})
    except Exception as e:
        logger.error("Error fetching buy/sell data for symbol %s: %s", symbol, e)
        logger.exception(e)
        return None

def get_x_label_align(x, x_max_current):
    if x > x_max_current*0.9:
        return (x_max_current*0.99, 'right')
    else:
        return (max(x, x_max_current*0.01), 'left')

def get_tw_stock_candles_png(symbol: str, save_to_local_file: bool = True) -> str | None:
    try:
        stock_info = get_tw_stock_price(symbol)
        if not stock_info:
            return None

        ticker = quote_stock_ticker(symbol)
        resp = quote_stock_candles(symbol)
        previous_close = ticker.get('previousClose')
        title_info = get_info_for_day_candle_picture(stock_info)
        candles = resp.get("data", [])

        if not candles:
            logger.warning("Fugle candles response missing data for %s: %s", symbol, resp)
            return None

        df = pd.DataFrame(candles)
        df["time"] = pd.to_datetime(df["date"])
        df = df.set_index("time")
        df = df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
        )

        market_colors = mpf.make_marketcolors(
            up="#8fb3ff",
            down="#8fb3ff",
            edge="#8fb3ff",
            wick="#8fb3ff",
            volume="#8fb3ff",
        )

        font_name = "Noto Sans TC"
        if FONT_PATH.exists():
            try:
                fm.fontManager.addfont(str(FONT_PATH))
                chinese_font_prop = fm.FontProperties(fname=FONT_PATH)
                font_name = chinese_font_prop.get_name()
            except Exception as exc:
                logger.warning("Failed to load font %s: %s", FONT_PATH, exc)

        dark_blue_style = mpf.make_mpf_style(
            base_mpf_style="nightclouds",
            marketcolors=market_colors,
            facecolor="#0b1b3b",
            gridcolor="#1f2f57",
            rc={ 'font.family': font_name }
        )

        addplots = []
        if previous_close is not None:
            close_series = df["Close"]
            above = close_series.where(close_series > previous_close)
            equal = close_series.where(close_series == previous_close)
            below = close_series.where(close_series < previous_close)

            if not above.isna().all():
                addplots.append(mpf.make_addplot(above, type="line", color='red', width=1))
            if not equal.isna().all():
                addplots.append(mpf.make_addplot(equal, type="line", color='#8e8989', width=1))
            if not below.isna().all():
                addplots.append(mpf.make_addplot(below, type="line", color='green', width=1))

        high_idx = df["High"].idxmax() 
        high_val = df.loc[high_idx, "High"]
        low_idx = df["Low"].idxmin()
        low_val = df.loc[low_idx, "Low"]
        limit_up_price = previous_close*1.1
        limit_down_price = previous_close*0.9

        if ticker['exchange'] == "TPEx" or ticker['type'] == "INDEX":
            high_val_diff = high_val - previous_close
            low_val_diff = previous_close - low_val
            bound = max(high_val_diff, low_val_diff)*1.5
            if bound > 0:
                limit_up_price = previous_close + bound
                limit_down_price = previous_close - bound
        elif 'limitUpPrice' in ticker and 'limitDownPrice' in ticker:
            limit_up_price = ticker.get("limitUpPrice")
            limit_down_price = ticker.get("limitDownPrice")

        start = min(df.index[0] - pd.Timedelta(minutes=1), df.index[0].replace(hour=9, minute=0, second=0, microsecond=0))
        end = max(df.index[-1] + pd.Timedelta(minutes=1), df.index[-1].replace(hour=13, minute=30, second=0, microsecond=0))
        xlim = (start, end)
        y_pad = (limit_up_price - limit_down_price) * 0.003
        ylim = (limit_down_price - y_pad, limit_up_price + y_pad)

        fig, axes = mpf.plot(
            df,
            type="line",
            volume=True,
            xlim=xlim,
            ylim=ylim,
            addplot=addplots,
            style=dark_blue_style,
            returnfig=True,
            tight_layout=True,
            scale_padding={'left': 0.6, 'top': 4, 'right': 1, 'bottom': 0.6}
        )

        ax = fig.axes[0]
        ax.axhline(previous_close, color="#8e8989", linestyle="-", linewidth=0.5) # previous close price line

        # draw labels of highest and lowest price
        x_min_current, x_max_current = ax.get_xlim()
        y_min_current, y_max_current = ax.get_ylim()
        y_span = y_max_current - y_min_current
        y_pad = max(y_span * 0.05, 0.01)

        high_text_y = min(high_val + y_pad, y_max_current - y_pad)
        low_text_y = max(low_val - y_pad, y_min_current + y_pad)

        high_low_value_bbox_style = dict(facecolor="#01050A54", edgecolor="none", boxstyle="square,pad=0.4")
        if high_val == low_val:
            if high_val > previous_close:
                (high_x, high_ha) = get_x_label_align(df['High'].argmax(), x_max_current)
                ax.text(high_x, high_text_y, f"最高價: {high_val:.2f}", ha=high_ha, va='center', fontsize=10, bbox=high_low_value_bbox_style, color='white', clip_on=False)
            else:
                (low_x, low_ha) = get_x_label_align(df['Low'].argmin(), x_max_current)
                ax.text(low_x, low_text_y, f"最低價: {low_val:.2f}", ha=low_ha, va='center', fontsize=10, bbox=high_low_value_bbox_style, color='white', clip_on=False)
        else:
            (high_x, high_ha) = get_x_label_align(df['High'].argmax(), x_max_current)
            (low_x, low_ha) = get_x_label_align(df['Low'].argmin(), x_max_current)
            ax.text(high_x, high_text_y, f"最高價: {high_val:.2f}", ha=high_ha, va='center', fontsize=10, bbox=high_low_value_bbox_style, color='white', clip_on=False)
            ax.text(low_x, low_text_y, f"最低價: {low_val:.2f}", ha=low_ha, va='center', fontsize=10, bbox=high_low_value_bbox_style, color='white', clip_on=False)

        # hide y and volume's label
        ax.yaxis.label.set_visible(False)
        axes[2].set_ylabel("")

        for axis in fig.axes:
            axis.tick_params(axis="x", labelrotation=0)

        if title_info:
            fig.suptitle(title_info["title"], x=fig.subplotpars.left - 0.06, ha='left', y=0.97)
            fig.text(0.065, 0.90, title_info['price'], color=title_info['color'], fontsize=12)

        fig.patch.set_facecolor("#0b1b3b")

        image_name = f"{symbol}_{round(time.time())}.jpg"
        if save_to_local_file:
            project_root = Path(__file__).resolve().parents[2]
            output_path = project_root / f"{image_name}"
            fig.savefig(str(output_path), format="jpg", facecolor=fig.get_facecolor(), dpi=300)
            return str(output_path)
        else:
            buffer = io.BytesIO()
            fig.savefig(buffer, format="jpg", facecolor=fig.get_facecolor(), dpi=300)
            buffer.seek(0)
            presign_url = put_image(image_name, buffer.getvalue())
            print(f"Rely image url={presign_url}")
            return presign_url
    except Exception as exc:
        logger.error("Fugle candle API error for %s: %s", symbol, exc)
        logger.exception(exc)
        return None
