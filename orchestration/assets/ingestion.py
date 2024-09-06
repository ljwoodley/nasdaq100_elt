import yfinance as yf
import pandas as pd
import requests

from bs4 import BeautifulSoup
from io import StringIO

from dagster_duckdb import DuckDBResource
from dagster import asset


@asset(compute_kind="python", group_name="ingestion")
def nasdaq100_tickers() -> list:
    """Nasdaq-100 tickers scraped from Wikipedia."""

    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    table_class = "wikitable sortable"
    table_id = "constituents"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        html_table = soup.find('table', {'class': table_class, 'id': table_id})

        if html_table:
            table_io = StringIO(html_table.prettify())
            nasdaq_holdings = pd.read_html(table_io)[0]
            nasdaq_holdings = nasdaq_holdings[nasdaq_holdings['Ticker'] != 'GOOG']
            nasdaq100_tickers = nasdaq_holdings['Ticker'].tolist()
            return nasdaq100_tickers
        else:
            print("Table not found.")
            return None
    else:
        print("Failed to retrieve webpage.")
        return None


@asset(
    compute_kind="python",
    group_name="ingestion"
)
def nasdaq100_holdings_ytd_performance(nasdaq100_tickers: list, database: DuckDBResource) -> None:
    """
    YTD performance data for NASDAQ-100 companies, loaded to the database.
    """

    raw_data = []

    for ticker in nasdaq100_tickers:
        stock = yf.Ticker(ticker)
        try:
            ytd_data = stock.history(period="ytd")

            if not ytd_data.empty:
                # First day close price of the year
                start_price = ytd_data['Close'].iloc[0]
                # Most recent close price
                last_price = ytd_data['Close'].iloc[-1]
                ytd_change = round(
                    ((last_price - start_price) / start_price) * 100, 2)
            else:
                ytd_change = None

            company_name = stock.info.get('shortName')
            industry = stock.info.get('industry')
            sector = stock.info.get('sector')
            market_cap = stock.info.get('marketCap')

            raw_data.append([company_name, ticker, industry,
                            sector, ytd_change, last_price, market_cap])

        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {str(e)}")

    columns = ['company_name',
               'ticker',
               'industry',
               'sector',
               'ytd_change',
               'last_price',
               'market_cap']

    table_to_load = pd.DataFrame(raw_data, columns=columns)

    query = """
        create table if not exists nasdaq100_holdings(
            company_name varchar,
            ticker varchar(10),
            industry varchar,
            sector varchar,
            ytd_change float,
            last_price float,
            market_cap float
        );
        """

    with database.get_connection() as conn:
        conn.execute(query)
        conn.execute("truncate table nasdaq100_holdings")
        conn.register("table_to_load", table_to_load)
        conn.execute(
            "insert into nasdaq100_holdings select * from table_to_load")


@asset(compute_kind="python", group_name="ingestion")
def nasdaq100_daily_ohlc(database: DuckDBResource) -> None:
    """
    Daily open, high, low, close (ohlc) prices for NASDAQ-100 futures, loaded to the database.
    """

    raw_data = yf.download("NQ=F", period='max')

    table_to_load = (
        raw_data
        .drop(columns=['Adj Close', 'Volume'])
        .reset_index()
        .rename(columns=str.lower)
        .query("date >= '2001-01-01'")
    )

    create_table_query = """
        create table if not exists nasdaq100_daily_ohlc(
            date date not null primary key,
            open float,
            high float,
            low float,
            close float
        );
        """

    insert_query = """
        insert into nasdaq100_daily_ohlc 
        select * from table_to_load
        where cast(date as date) not in (select date from nasdaq100_daily_ohlc);
    """

    with database.get_connection() as conn:
        conn.execute(create_table_query)
        conn.register("table_to_load", table_to_load)
        conn.execute(insert_query)
