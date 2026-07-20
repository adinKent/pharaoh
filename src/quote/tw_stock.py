import csv
import logging
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from io import StringIO
from zoneinfo import ZoneInfo

import mplfinance as mpf
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from pymongo import UpdateOne

from quote.chart_common import draw_turnover_header, get_x_label_align, load_chart_font_name, save_or_upload_fig
from quote.chart_theme import get_chart_theme
from quote.fugle import (
    quote_stock as fugle_quote_stock,
)
from quote.fugle import (
    quote_stock_candles,
    quote_stock_ticker,
)
from quote.output import format_price_output, get_info_for_day_candle_picture
from utils.aws_helper import is_running_on_lambda
from utils.mongo_helper import get_mongo_client

logger = logging.getLogger(__name__)

TWSE_EX_DIVIDEND_URL = "https://openapi.twse.com.tw/v1/exchangeReport/TWT48U_ALL"
TPEX_EX_DIVIDEND_URL = "https://www.tpex.org.tw/openapi/v1/tpex_exright_prepost"


def get_tw_stock_price(symbol: str, period: str | None = None, yf_symbol: str | None = None) -> dict | None:
    """
    Get real-time stock price for a Taiwan stock symbol using fugle and yfinance library.
    Returns a dict with price info or None if not found.
    """
    try:
        stock_info = fugle_quote_stock(symbol)
        if stock_info:
            previous_close = stock_info.get("previousClose") or stock_info.get("referencePrice")
            current_price = stock_info.get("lastPrice") or stock_info.get("closePrice") or previous_close

            yf_format_stock_info = {
                "exchange": stock_info.get("exchange") or "TWSE",
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

            return format_price_output(symbol, yf_format_stock_info, history)
    except ImportError:
        # Fallback to simple web scraping if yfinance not available
        return _fallback_stock_price(symbol)
    except Exception as e:
        logger.error("Error fetching tw stock price: %s", e)
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


def get_today_ex_dividend_stocks() -> tuple[list[dict], str]:
    query_date = datetime.now(ZoneInfo("Asia/Taipei")).date()
    roc_date = _to_roc_date(query_date)
    display_date = query_date.strftime("%Y-%m-%d")

    stocks = []
    stocks.extend(get_twse_ex_dividend_stocks(roc_date) or [])
    stocks.extend(get_tpex_ex_dividend_stocks(roc_date) or [])
    stocks.sort(key=lambda stock: (stock.get("market", ""), stock.get("symbol", "")))

    return stocks, display_date


def _to_roc_date(date) -> str:
    return f"{date.year - 1911:03d}{date.month:02d}{date.day:02d}"


def get_twse_ex_dividend_stocks(roc_date: str) -> list[dict] | None:
    try:
        resp = requests.get(TWSE_EX_DIVIDEND_URL, timeout=10)
        resp.raise_for_status()
        return [
            _normalize_twse_ex_dividend_row(row)
            for row in resp.json()
            if row.get("Date") == roc_date and _is_ex_dividend_type(row.get("Exdividend", ""))
        ]
    except Exception as e:
        logger.error("Error fetching TWSE ex-dividend data: %s", e)
        logger.exception(e)
        return None


def get_tpex_ex_dividend_stocks(roc_date: str) -> list[dict] | None:
    try:
        resp = requests.get(TPEX_EX_DIVIDEND_URL, timeout=10)
        resp.raise_for_status()
        return [
            _normalize_tpex_ex_dividend_row(row)
            for row in resp.json()
            if row.get("ExRrightsExDividendDate") == roc_date and _is_ex_dividend_type(row.get("ExRrightsExDividend", ""))
        ]
    except Exception as e:
        logger.error("Error fetching TPEx ex-dividend data: %s", e)
        logger.exception(e)
        return None


def _is_ex_dividend_type(value: str) -> bool:
    return "息" in value


def _normalize_twse_ex_dividend_row(row: dict) -> dict:
    return {
        "date": row.get("Date", ""),
        "market": "上市",
        "symbol": row.get("Code", ""),
        "name": row.get("Name", ""),
        "type": row.get("Exdividend", ""),
        "cashDividend": row.get("CashDividend", ""),
    }


def _normalize_tpex_ex_dividend_row(row: dict) -> dict:
    return {
        "date": row.get("ExRrightsExDividendDate", ""),
        "market": "上櫃",
        "symbol": row.get("SecuritiesCompanyCode", ""),
        "name": row.get("CompanyName", ""),
        "type": row.get("ExRrightsExDividend", ""),
        "cashDividend": row.get("CashDividend", ""),
    }


def _fallback_stock_price(symbol: str):
    """
    Fallback method using Taiwan Stock Exchange API or web scraping.
    """
    try:
        # Try Taiwan Stock Exchange API
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=json&stockNo={symbol}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("stat") == "OK" and data.get("data"):
                # Get the most recent data
                latest_data = data["data"][-1]
                price = float(latest_data[1])  # Close price

                return {
                    "symbol": symbol,
                    "name": f"Stock {symbol}",
                    "price": price,
                    "currency": "TWD",
                    "time": None,
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
            "response": "json",
            "date": "",  # Current month
            "stockNo": symbol,
        }
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()

            # Check if the response contains stock data
            if data.get("stat") == "OK":
                # The stock name is usually in the title field
                title = data.get("title", "")
                if title:
                    # Extract stock name from title, Format: "114年10月 2884 玉山金           各日成交資訊"

                    parts = title.split()
                    if len(parts) >= 4:
                        stock_name = parts[-2]
                        return stock_name

        # Alternative API endpoint for company basic info
        alt_url = "https://www.twse.com.tw/rwd/zh/company/codeQuery"
        alt_params = {"STK_NO": symbol}

        resp = requests.get(alt_url, params=alt_params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()

            # Extract company name from response
            if "data" in data and data["data"]:
                for item in data["data"]:
                    if len(item) >= 2 and item[0] == symbol:
                        return item[1]  # Company name is usually in the second column

        # Try another endpoint for listed companies
        list_url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL"
        list_params = {"response": "json"}

        resp = requests.get(list_url, params=list_params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()

            if data.get("stat") == "OK" and "data" in data:
                for stock_data in data["data"]:
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
            if "info" in data:
                return data["info"].get("shortName", None)  # for stock

            return data.get("shortName", None)  # for ETF
    except Exception as e:
        logger.error(f"Error fetching Taiwan stock name for {symbol} from tpex: {e}")
        logger.exception(e)

    return None


def get_tw_stock_symbol_from_company_name(company_name: str):
    url = "https://mopsov.twse.com.tw/mops/web/ajax_autoComplete"
    encoded_company_name = urllib.parse.quote(company_name)
    payload = (
        f"encodeURIComponent=1&step=1&firstin=ture&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&"
        f"inpuType=co_id&TYPEK=all&co_id={encoded_company_name}&sstep=1"
    )

    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code == 200:
            # Parse HTML
            soup = BeautifulSoup(resp.content, "html.parser")

            elements = soup.find_all(id=re.compile(r"^autoDiv-\d+$"))
            if not elements:
                logger.warning("Taiwan stock symbol for name %s not found from twse", company_name)
                return None

            exact_match = next(
                (
                    element
                    for element in elements
                    if _normalize_company_name(_extract_autocomplete_company_name(element)) == _normalize_company_name(company_name)
                ),
                None,
            )
            element = exact_match or elements[0]
            if element.has_attr("value"):
                return element["value"]

            logger.warning("Taiwan stock symbol for name %s not found from twse", company_name)
            return None

    except Exception as e:
        logger.error(
            "Error fetching Taiwan stock symbol for name %s from twse: %s",
            company_name,
            e,
        )
        logger.exception(e)

    return None


def _normalize_company_name(company_name: str) -> str:
    return re.sub(r"\s+", "", company_name)


def _extract_autocomplete_company_name(element) -> str:
    text = element.get_text(" ", strip=True)
    if not text and element.parent:
        text = element.parent.get_text(" ", strip=True)

    stock_symbol = str(element.get("value", "")).strip()
    if stock_symbol and text.startswith(stock_symbol):
        return text[len(stock_symbol) :].strip()

    return re.sub(r"^\s*\d+[A-Za-z]*\s*", "", text).strip()


def format_total_net_diff(field_name, amount):
    result = amount
    if "差額" in field_name:
        amount_number = float(amount)
        if amount_number > 0:
            result = f"+{amount_number}"

    return result


def format_twse_buy_and_sell_result(bug_sell_data: dict) -> str | None:
    """
    Format TWSE fund result JSON to a pretty text.
    """
    if not bug_sell_data or bug_sell_data.get("stat") != "OK":
        return None

    fields = bug_sell_data.get("fields", [])
    data = bug_sell_data.get("data", [])
    title = bug_sell_data.get("title", "")
    notes = bug_sell_data.get("notes", [])
    hints = bug_sell_data.get("hints", "")

    # Convert numeric columns (except the first column) to units of 100 million
    converted_data = []
    for row in data:
        new_row = [row[0]]
        for cell in row[1:]:
            try:
                num = float(cell.replace(",", ""))
                new_cell = f"{num / 100_000_000:.2f}"
            except Exception:
                new_cell = cell
            new_row.append(new_cell)
        converted_data.append(new_row)

    lines = []
    if title:
        lines += [title, ""]

    foreign_row = converted_data[3]
    for i in range(1, len(foreign_row)):
        field_name = fields[i]
        amount = format_total_net_diff(field_name, foreign_row[i])
        lines.append(f"外資{fields[i]}:{amount.rjust(8)}")

    lines.append("")  # separator

    for row in [
        converted_data[2],
        converted_data[0],
        converted_data[1],
        converted_data[5],
    ]:  # 投信、自營商(自行買賣)、自營商(避險)、合計
        for i in range(1, len(row)):
            field_name = fields[i]
            amount = format_total_net_diff(field_name, row[i])
            lines.append(f"{row[0]}{field_name}:{amount.rjust(8)}")
        lines.append("")

    lines.append("單位：億元")

    return "\n".join(lines)


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
    today = get_effective_date().strftime("%Y%m%d")
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
    today = get_effective_date().strftime("%Y%m%d")
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
            if "證券代號" in line:
                data_started = True
            if data_started and line.strip():
                if "說明" in line:  # data end
                    break
                else:
                    csv_content.append(line)

        reader = csv.DictReader(StringIO("\n".join(csv_content)))
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
    today = urllib.parse.quote(get_effective_date().strftime("%Y-%m-%d"))
    url = f"https://www.tpex.org.tw/www/zh-tw/insti/dailyTrade?type=Daily&sect=AL&date={today}id=&response=csv"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        # The response text contains informational headers and footers.
        lines = resp.text.splitlines()
        csv_content = []
        data_started = False
        for line in lines:
            if "代號" in line and "名稱" in line:
                data_started = True
            if data_started and line.strip():
                if re.search(r"共\d+筆", line):  # data end
                    break
                else:
                    csv_content.append(line)

        reader = csv.DictReader(StringIO("\n".join(csv_content)))
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
                db = client["TaiwanMarket"]
                collection = db["buyAndSell"]
            except Exception as e:
                logger.error("Failed to connect to MongoDB: %s", e)
                logger.exception(e)
                return (0, 0)

            trade_date = get_effective_date().strftime("%Y-%m-%d")
            db_bulk_operations = []
            twse_result = get_twse_buy_sell_today_result()
            if twse_result:
                for row in twse_result:
                    doc = normalize_twse_stock_buy_sell_to_db_format(row)
                    doc["date"] = trade_date
                    doc["market"] = "TWSE"
                    db_bulk_operations.append(UpdateOne({"_id": doc["symbol"]}, {"$set": doc}, upsert=True))

            tpex_result = get_tpex_buy_sell_today_result()
            if tpex_result:
                for row in tpex_result:
                    doc = normalize_tpex_stock_buy_sell_to_db_format(row)
                    doc["date"] = trade_date
                    doc["market"] = "TPEX"
                    db_bulk_operations.append(UpdateOne({"_id": doc["symbol"]}, {"$set": doc}, upsert=True))

            if len(db_bulk_operations) > 0:
                result = collection.bulk_write(db_bulk_operations)
                matched_count = result.matched_count
                upserted_count = result.upserted_count
                logger.info(
                    "Synced to DB. Matched: %s, Upserted: %s",
                    result.matched_count,
                    result.upserted_count,
                )
    except Exception as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        logger.exception(e)

    return (matched_count, upserted_count)


def normalize_twse_stock_buy_sell_to_db_format(row: dict) -> dict:
    """
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
    """

    return {
        "symbol": re.sub(r'[="\s]', "", row["證券代號"]),
        "name": re.sub(r'[="\s]', "", row["證券名稱"]),
        "foreignBuy": row["外陸資買進股數(不含外資自營商)"],
        "foreignSell": row["外陸資賣出股數(不含外資自營商)"],
        "foreignNet": row["外陸資買賣超股數(不含外資自營商)"],
        "foreignDealerBuy": row["外資自營商買進股數"],
        "foreignDealerSell": row["外資自營商賣出股數"],
        "foreignDealerNet": row["外資自營商買賣超股數"],
        "investTrustBuy": row["投信買進股數"],
        "investTrustSell": row["投信賣出股數"],
        "investTrustNet": row["投信買賣超股數"],
        "dealerTotalNet": row["自營商買賣超股數"],
        "dealerBuy": row["自營商買進股數(自行買賣)"],
        "dealerSell": row["自營商賣出股數(自行買賣)"],
        "dealerNet": row["自營商買賣超股數(自行買賣)"],
        "dealerHedgeBuy": row["自營商買進股數(避險)"],
        "dealerHedgeSell": row["自營商賣出股數(避險)"],
        "dealerHedgeNet": row["自營商買賣超股數(避險)"],
        "totalNet": row["三大法人買賣超股數"],
    }


def normalize_tpex_stock_buy_sell_to_db_format(row: dict) -> dict:
    """
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
    """

    return {
        "symbol": re.sub(r'[="\s]', "", row["代號"]),
        "name": re.sub(r'[="\s]', "", row["名稱"]),
        "foreignBuy": row["外資及陸資(不含外資自營商)-買進股數"],
        "foreignSell": row["外資及陸資(不含外資自營商)-賣出股數"],
        "foreignNet": row["外資及陸資(不含外資自營商)-買賣超股數"],
        "foreignDealerBuy": row["外資自營商-買進股數"],
        "foreignDealerSell": row["外資自營商-賣出股數"],
        "foreignDealerNet": row["外資自營商-買賣超股數"],
        "foreignTotalBuy": row["外資及陸資-買進股數"],
        "foreignTotalSell": row["外資及陸資-賣出股數"],
        "foreignTotalNet": row["外資及陸資-買賣超股數"],
        "investTrustBuy": row["投信-買進股數"],
        "investTrustSell": row["投信-賣出股數"],
        "investTrustNet": row["投信-買賣超股數"],
        "dealerBuy": row["自營商(自行買賣)-買進股數"],
        "dealerSell": row["自營商(自行買賣)-賣出股數"],
        "dealerNet": row["自營商(自行買賣)-買賣超股數"],
        "dealerHedgeBuy": row["自營商(避險)-買進股數"],
        "dealerHedgeSell": row["自營商(避險)-賣出股數"],
        "dealerHedgeNet": row["自營商(避險)-買賣超股數"],
        "dealerTotalBuy": row["自營商-買進股數"],
        "dealerTotalSell": row["自營商-賣出股數"],
        "dealerTotalNet": row["自營商-買賣超股數"],
        "totalNet": row["三大法人買賣超股數合計"],
    }


def get_symbol_buy_sell_today_result(symbol: str) -> dict | None:
    try:
        with get_mongo_client() as client:
            db = client["TaiwanMarket"]
            collection = db["buyAndSell"]
            return collection.find_one({"_id": symbol})
    except Exception as e:
        logger.error("Error fetching buy/sell data for symbol %s: %s", symbol, e)
        logger.exception(e)
        return None


def _format_trade_value(trade_value: float) -> str:
    """Format a TWD trade value with a Chinese unit: 億 (1e8) once it reaches 億, else 萬 (1e4).

    Keeps one decimal for small amounts; rounds to an integer once it reads in the hundreds.
    """
    if trade_value >= 1e8:
        yi = trade_value / 1e8
        return f"{yi:,.0f} 億" if yi >= 100 else f"{yi:,.1f} 億"
    wan = trade_value / 1e4
    return f"{wan:,.0f} 萬" if wan >= 100 else f"{wan:,.1f} 萬"


def get_tw_stock_candles_png(symbol: str, save_to_local_file: bool | None = None) -> str | None:
    if save_to_local_file is None:
        # On Lambda, upload to S3 (LINE needs a public URL); locally, save a file to inspect.
        save_to_local_file = not is_running_on_lambda()
    try:
        stock_info = get_tw_stock_price(symbol)

        if not stock_info:
            return None

        ticker = quote_stock_ticker(symbol)
        resp = quote_stock_candles(symbol)
        previous_close = ticker.get("previousClose")
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

        theme = get_chart_theme()
        market_colors = mpf.make_marketcolors(
            up=theme.intraday_mark,
            down=theme.intraday_mark,
            edge=theme.intraday_mark,
            wick=theme.intraday_mark,
            volume=theme.intraday_mark,
        )

        font_name = load_chart_font_name()

        chart_style = mpf.make_mpf_style(
            base_mpf_style=theme.base_mpf_style,
            marketcolors=market_colors,
            facecolor=theme.surface,
            gridcolor=theme.grid,
            rc={"font.family": font_name},
        )

        addplots = []
        if previous_close is not None:
            close_series = df["Close"]
            above = close_series.where(close_series > previous_close)
            equal = close_series.where(close_series == previous_close)
            below = close_series.where(close_series < previous_close)

            if not above.isna().all():
                addplots.append(mpf.make_addplot(above, type="line", color=theme.up, width=1))
            if not equal.isna().all():
                addplots.append(mpf.make_addplot(equal, type="line", color=theme.flat, width=1))
            if not below.isna().all():
                addplots.append(mpf.make_addplot(below, type="line", color=theme.down, width=1))

        high_idx = df["High"].idxmax()
        high_val = df.loc[high_idx, "High"]
        low_idx = df["Low"].idxmin()
        low_val = df.loc[low_idx, "Low"]
        limit_up_price = previous_close * 1.1
        limit_down_price = previous_close * 0.9

        if ticker["exchange"] == "TPEx" or ticker["type"] == "INDEX":
            high_val_diff = high_val - previous_close
            low_val_diff = previous_close - low_val
            bound = max(high_val_diff, low_val_diff) * 1.5
            if bound > 0:
                limit_up_price = previous_close + bound
                limit_down_price = previous_close - bound
        elif "limitUpPrice" in ticker and "limitDownPrice" in ticker:
            limit_up_price = ticker.get("limitUpPrice")
            limit_down_price = ticker.get("limitDownPrice")

        start = min(
            df.index[0] - pd.Timedelta(minutes=1),
            df.index[0].replace(hour=9, minute=0, second=0, microsecond=0),
        )
        end = max(
            df.index[-1] + pd.Timedelta(minutes=1),
            df.index[-1].replace(hour=13, minute=30, second=0, microsecond=0),
        )
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
            style=chart_style,
            returnfig=True,
            tight_layout=True,
            scale_padding={"left": 0.6, "top": 4, "right": 1, "bottom": 0.6},
        )

        ax = fig.axes[0]
        ax.axhline(previous_close, color=theme.flat, linestyle="-", linewidth=0.5)  # previous close price line

        # draw labels of highest and lowest price
        x_min_current, x_max_current = ax.get_xlim()
        y_min_current, y_max_current = ax.get_ylim()
        y_span = y_max_current - y_min_current
        y_pad = max(y_span * 0.05, 0.01)

        high_text_y = min(high_val + y_pad, y_max_current - y_pad)
        low_text_y = max(low_val - y_pad, y_min_current + y_pad)

        high_low_value_bbox_style = dict(facecolor=theme.label_box, edgecolor="none", boxstyle="square,pad=0.4")
        if high_val == low_val:
            if high_val > previous_close:
                (high_x, high_ha) = get_x_label_align(df["High"].argmax(), x_max_current)
                ax.text(
                    high_x,
                    high_text_y,
                    f"最高價: {high_val:.2f}",
                    ha=high_ha,
                    va="center",
                    fontsize=10,
                    bbox=high_low_value_bbox_style,
                    color=theme.ink,
                    clip_on=False,
                )
            else:
                (low_x, low_ha) = get_x_label_align(df["Low"].argmin(), x_max_current)
                ax.text(
                    low_x,
                    low_text_y,
                    f"最低價: {low_val:.2f}",
                    ha=low_ha,
                    va="center",
                    fontsize=10,
                    bbox=high_low_value_bbox_style,
                    color=theme.ink,
                    clip_on=False,
                )
        else:
            (high_x, high_ha) = get_x_label_align(df["High"].argmax(), x_max_current)
            (low_x, low_ha) = get_x_label_align(df["Low"].argmin(), x_max_current)
            ax.text(
                high_x,
                high_text_y,
                f"最高價: {high_val:.2f}",
                ha=high_ha,
                va="center",
                fontsize=10,
                bbox=high_low_value_bbox_style,
                color=theme.ink,
                clip_on=False,
            )
            ax.text(
                low_x,
                low_text_y,
                f"最低價: {low_val:.2f}",
                ha=low_ha,
                va="center",
                fontsize=10,
                bbox=high_low_value_bbox_style,
                color=theme.ink,
                clip_on=False,
            )

        # hide y and volume's label
        ax.yaxis.label.set_visible(False)
        axes[2].set_ylabel("")

        for axis in fig.axes:
            axis.tick_params(axis="x", labelrotation=0)

        if title_info:
            fig.suptitle(title_info["title"], x=fig.subplotpars.left - 0.06, ha="left", y=0.97)
            fig.text(0.065, 0.90, title_info["price"], color=title_info["color"], fontsize=12)

        # Trade turnover in the top-right. Stock: 成交 volume (張) + 總量 value (億/萬).
        # Index: single 總量 line — the market's turnover value in 億 is colloquially its "量".
        total = (fugle_quote_stock(symbol) or {}).get("total") or {}
        trade_volume = total.get("tradeVolume")
        trade_value = total.get("tradeValue")
        is_index = ticker.get("type") == "INDEX"
        turnover_rows = []  # (label, number, unit, row_color)
        if is_index:
            if trade_value is not None:
                turnover_rows.append(("總量", *_format_trade_value(trade_value).rsplit(" ", 1), None))
        else:
            if trade_volume is not None:
                # 成交 is a distinct accent (whole row), not part of the muted/bright hierarchy.
                turnover_rows.append(("成交", f"{trade_volume:,}", "張", theme.stat_accent))
            if trade_value is not None:
                turnover_rows.append(("總量", *_format_trade_value(trade_value).rsplit(" ", 1), None))
        draw_turnover_header(fig, turnover_rows, theme, font_name)

        fig.patch.set_facecolor(theme.surface)
        return save_or_upload_fig(fig, f"{symbol}_{round(time.time())}.jpg", save_to_local_file)
    except Exception as exc:
        logger.error("Fugle candle API error for %s: %s", symbol, exc)
        logger.exception(exc)
        return None


def get_tw_stock_year_candles_png(symbol: str, save_to_local_file: bool | None = None) -> str | None:
    if save_to_local_file is None:
        # On Lambda, upload to S3 (LINE needs a public URL); locally, save a file to inspect.
        save_to_local_file = not is_running_on_lambda()
    try:
        stock_info = get_tw_stock_price(symbol)
        if not stock_info:
            return None

        ticker = fugle_quote_stock(symbol)
        title_info = get_info_for_day_candle_picture(stock_info)

        yahoo_symbol = f"{symbol}.TW"
        if ticker and ticker["exchange"] == "TPEx":
            yahoo_symbol = f"{symbol}.TWO"
        elif ticker and ticker["type"] == "INDEX":
            if symbol == "IX0001":
                yahoo_symbol = "^TWII"
            elif symbol == "IX0043":
                yahoo_symbol = "IX0043.TWO"

        df = yf.Ticker(yahoo_symbol).history(period="6mo")
        if df.empty:
            logger.warning("No 1-year history found for %s", yahoo_symbol)
            return None

        # season/month/day lines in TW charts usually map to MA60/20/5.
        ma_windows = {
            "日線(5MA)": 5,
            "月線(20MA)": 20,
            "季線(60MA)": 60,
        }
        theme = get_chart_theme()
        ma_colors = {
            "日線(5MA)": theme.ma5,
            "月線(20MA)": theme.ma20,
            "季線(60MA)": theme.ma60,
        }
        ma_series: dict[str, pd.Series] = {name: df["Close"].rolling(window=window, min_periods=window).mean() for name, window in ma_windows.items()}
        ma_addplots = [mpf.make_addplot(ma_series[name], type="line", color=ma_colors[name], width=1.1, panel=0) for name in ma_windows]

        market_colors = mpf.make_marketcolors(
            up=theme.up,
            down=theme.down,
            wick={"up": theme.up, "down": theme.down},
            edge="inherit",
            volume="inherit",
        )

        font_name = load_chart_font_name()

        chart_style = mpf.make_mpf_style(
            base_mpf_style=theme.base_mpf_style,
            marketcolors=market_colors,
            facecolor=theme.surface,
            gridcolor=theme.grid,
            rc={"font.family": font_name},
        )

        y_min_current = df.get("Low").min()
        y_max_current = df.get("High").max()
        y_span = y_max_current - y_min_current
        y_pad = max(y_span * 0.1, 0.01)
        new_y_lim = (y_min_current - y_pad, y_max_current + y_pad)

        fig, axes = mpf.plot(
            df,
            type="candle",
            volume=True,
            ylim=new_y_lim,
            addplot=ma_addplots,
            datetime_format="%Y-%m-%d",
            style=chart_style,
            returnfig=True,
            tight_layout=True,
            scale_padding={"left": 0.6, "top": 4, "right": 1, "bottom": 0.6},
        )

        ax = fig.axes[0]
        # Keep MA lines below candlesticks.
        for line in ax.lines:
            line.set_zorder(1)
        for collection in ax.collections:
            collection.set_zorder(2)

        high_idx = df["High"].idxmax()
        high_val = df.loc[high_idx, "High"]
        low_idx = df["Low"].idxmin()
        low_val = df.loc[low_idx, "Low"]

        # draw labels of highest and lowest price
        x_min_current, x_max_current = ax.get_xlim()
        # y_min_current, y_max_current = ax.get_ylim()
        # y_span = y_max_current - y_min_current
        # y_pad = max(y_span * 0.05, 0.01)

        low_text_y = low_val - y_pad * 0.7
        high_text_y = high_val + y_pad * 0.7

        high_low_value_bbox_style = dict(facecolor=theme.label_box, edgecolor="none", boxstyle="square,pad=0.4")

        (high_x, high_ha) = get_x_label_align(df["High"].argmax(), x_max_current)
        (low_x, low_ha) = get_x_label_align(df["Low"].argmin(), x_max_current)
        ax.text(
            high_x,
            high_text_y,
            f"最高價: {high_val:.2f}",
            ha=high_ha,
            va="top",
            fontsize=10,
            bbox=high_low_value_bbox_style,
            color=theme.ink,
            clip_on=False,
        )
        ax.text(
            low_x,
            low_text_y,
            f"最低價: {low_val:.2f}",
            ha=low_ha,
            va="bottom",
            fontsize=10,
            bbox=high_low_value_bbox_style,
            color=theme.ink,
            clip_on=False,
        )

        legend_handles = [
            ax.plot([], [], color=ma_colors[name], linewidth=1.2, label=f"{name}: {ma_series[name].dropna().iloc[-1]:.2f}")[0]
            for name in ma_windows
            if not ma_series[name].dropna().empty
        ]
        if legend_handles:
            ax.legend(
                handles=legend_handles,
                loc="upper left",
                fontsize=9,
                frameon=True,
                facecolor=theme.surface,
                edgecolor=theme.grid,
                labelcolor=theme.ink,
            )

        # hide y and volume's label
        ax.yaxis.label.set_visible(False)
        axes[2].set_ylabel("")

        for axis in fig.axes:
            axis.tick_params(axis="x", labelrotation=0)

        if title_info:
            fig.suptitle(title_info["title"], x=fig.subplotpars.left - 0.06, ha="left", y=0.97)
            fig.text(0.065, 0.90, title_info["price"], color=title_info["color"], fontsize=12)

        fig.patch.set_facecolor(theme.surface)
        return save_or_upload_fig(fig, f"{symbol}_1y_{round(time.time())}.jpg", save_to_local_file)
    except Exception as exc:
        logger.error("Error generating 1y candle chart for %s: %s", symbol, exc)
        logger.exception(exc)
        return None
