"""Download historical data from Yahoo Finance.

Usage:
    pip install yfinance
    python scripts/download_yahoo_data.py
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def download_data(symbol, yahoo_ticker, start_date, end_date, output_file):
    """
    Download data from Yahoo Finance and save to CSV.
    
    Args:
        symbol: Our symbol (ES, NQ, etc.)
        yahoo_ticker: Yahoo Finance ticker (^GSPC, ^IXIC, etc.)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output_file: Output CSV filename
    """
    print(f"Downloading {symbol} data from Yahoo Finance...")
    print(f"Ticker: {yahoo_ticker}")
    print(f"Period: {start_date} to {end_date}")
    
    # Download data
    df = yf.download(yahoo_ticker, start=start_date, end=end_date, progress=False)
    
    if df.empty:
        print(f"Error: No data downloaded for {yahoo_ticker}")
        return
    
    # Rename columns to match our format
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    # Reset index to make date a column
    df = df.reset_index()
    df = df.rename(columns={'Date': 'date'})
    
    # Keep only required columns
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    # Format date as YYYY-MM-DD
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    print(f"✓ Downloaded {len(df)} bars")
    print(f"✓ Saved to: {output_file}")
    print(f"  Date range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}")
    print()


def main():
    """Download data for multiple instruments."""
    
    # Calculate date range (last 2 years)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    print("=" * 60)
    print("YAHOO FINANCE DATA DOWNLOADER")
    print("=" * 60)
    print(f"Date range: {start_date} to {end_date}\n")
    
    # Download data for each instrument
    # Note: Yahoo doesn't have futures data, so we use index proxies
    
    instruments = [
        {
            'symbol': 'ES',
            'yahoo_ticker': '^GSPC',  # S&P 500 Index
            'output': '/app/data/sample_data/ES_yahoo.csv'
        },
        {
            'symbol': 'NQ',
            'yahoo_ticker': '^IXIC',  # NASDAQ Composite
            'output': '/app/data/sample_data/NQ_yahoo.csv'
        },
        {
            'symbol': 'YM',
            'yahoo_ticker': '^DJI',   # Dow Jones
            'output': '/app/data/sample_data/YM_yahoo.csv'
        },
        {
            'symbol': 'RTY',
            'yahoo_ticker': '^RUT',   # Russell 2000
            'output': '/app/data/sample_data/RTY_yahoo.csv'
        },
        {
            'symbol': 'CL',
            'yahoo_ticker': 'CL=F',   # Crude Oil Futures
            'output': '/app/data/sample_data/CL_yahoo.csv'
        },
        {
            'symbol': 'GC',
            'yahoo_ticker': 'GC=F',   # Gold Futures
            'output': '/app/data/sample_data/GC_yahoo.csv'
        },
    ]
    
    for inst in instruments:
        try:
            download_data(
                symbol=inst['symbol'],
                yahoo_ticker=inst['yahoo_ticker'],
                start_date=start_date,
                end_date=end_date,
                output_file=inst['output']
            )
        except Exception as e:
            print(f"✗ Error downloading {inst['symbol']}: {e}\n")
    
    print("=" * 60)
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Ingest the data:")
    print("   python scripts/ingest_csv.py ES /app/data/sample_data/ES_yahoo.csv")
    print("   python scripts/ingest_csv.py NQ /app/data/sample_data/NQ_yahoo.csv")
    print("\n2. Check data:")
    print("   python scripts/check_data.py")
    print("\n3. Run backtest:")
    print("   python scripts/run_demo_backtest.py")


if __name__ == "__main__":
    # Check if yfinance is installed
    try:
        import yfinance
    except ImportError:
        print("Error: yfinance not installed")
        print("Install it with: pip install yfinance")
        exit(1)
    
    main()

