import polars as pl
from alpha_vantage.timeseries import TimeSeries
import os
import yaml
from time import sleep


script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
config_path = os.path.join(script_dir, 'config.yaml')  # Build the full path to config.yaml

# Function to load configuration from a YAML file
def load_config(file_path=config_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Fetch the API key and symbols from the config
def fetch_config_values():
    config = load_config()  # Load the config
    api_key = config.get('api_key')  # Access the API key
    symbols = config.get('symbols', {})  # Access the dictionary of symbols
    return api_key, symbols

# Function to get symbol metadata by symbol name
def get_symbol_metadata(symbol_name):
    _, symbols = fetch_config_values()  # Fetch symbols
    symbol_metadata = symbols.get(symbol_name)
    if symbol_metadata:
        return symbol_metadata
    else:
        return None  # Return None if symbol is not found


def fetch_and_save_stock_data(symbol: str, api_key: str, output_dir: str = "./stockdata") -> None:
    from datetime import datetime
    import os

    ts = TimeSeries(key=api_key, output_format='pandas')
    data, metadata = ts.get_daily(symbol=symbol, outputsize='full')

    # Convert to Polars
    data_pl = pl.DataFrame(data.reset_index())  # Reset to bring 'date' into a column
    metadata_pl = pl.DataFrame(metadata)

    # Rename data columns
    rename_mapping_data = {
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume'
    }
    data_pl = data_pl.rename(rename_mapping_data)

    # Add metadata fields as constant columns
    last_refreshed = metadata['3. Last Refreshed']
    time_zone = metadata['5. Time Zone']

    data_pl = data_pl.with_columns([
        pl.lit(symbol).alias("symbol"),
        pl.lit(last_refreshed).alias("last_refreshed"),
        pl.lit(time_zone).alias("time_zone")
    ])

    # Save CSVs
    os.makedirs(output_dir, exist_ok=True)
    data_path = f"{output_dir}/{symbol.upper()}_stockdata.csv"
    meta_path = f"{output_dir}/{symbol.upper()}_metadata.csv"

    data_pl.write_csv(data_path)
    print(f"Data for {symbol.upper()} saved to {data_path}")

if __name__ == '__main__':
    api_key, symbols = fetch_config_values()
    # for symbol in symbols:
    #     fetch_and_save_stock_data(symbol, api_key) 
    #     sleep(12)