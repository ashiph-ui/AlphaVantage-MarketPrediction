
import yaml
import pandas as pd
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Table, MetaData, Column, Integer, String, Date, Numeric, BigInteger


class DatabaseConnector:
    def __init__(self):
        self.engine = None
        self.creds = self.read_db_creds()

    def read_db_creds(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
        cred_path = os.path.join(script_dir, 'mydb_creds.yaml')  # Build the full path to config.yaml

        """Read the database credentials from a YAML file."""
        with open(cred_path, 'r') as file:
            creds = yaml.safe_load(file)
        return creds

    def init_db_engine(self, creds):
        """Initialise and return an SQLAlchemy database engine."""
        self.engine = create_engine(
            f"postgresql://{creds['RDS_USER']}:{creds['RDS_PASSWORD']}@"
            f"{creds['RDS_HOST']}:{creds['RDS_PORT']}/{creds['RDS_DATABASE']}"
        )
        return self.engine

    def list_db_tables(self, engine):
        """List all tables in the database."""
        inspector = inspect(engine)
        inspector.get_table_names()
        return inspector.get_table_names()
    def update_stock_data_from_csv(self, csv_path: str, table_name: str = 'stock_data'):
        """Load CSV data and update the database while avoiding duplicates."""

        # Pandas for SQLAlchemy
        df_new_pd = pd.read_csv(csv_path)

        # Check if table exists
        if self.engine.dialect.has_table(self.engine.connect(), table_name):
            df_existing = pd.read_sql(f"SELECT * FROM {table_name}", self.engine)
        else:
            df_existing = pd.DataFrame(columns=df_new_pd.columns)

        # Deduplicate based on 'date' and 'symbol'
        combined = pd.concat([df_existing, df_new_pd], ignore_index=True)
        combined = combined.drop_duplicates(subset=['date', 'symbol'])

        # Keep only new rows
        new_rows = combined[~combined.index.isin(df_existing.index)]
        if not new_rows.empty:
            new_rows.to_sql(table_name, con=self.engine, if_exists='append', index=False)
            print(f"Inserted {len(new_rows)} new rows into {table_name}")
        else:
            print("No new rows to insert.")


if __name__ == "__main__":
    db_connector = DatabaseConnector()
    creds = db_connector.read_db_creds()
    engine = db_connector.init_db_engine(creds)

    possible_folders = ['data/stockdata', './stockdata']
    csv_folder = None
    csv_files = []

    for folder in possible_folders:
        try:
            csv_files = [f for f in os.listdir(folder) if f.endswith('.csv')]
            csv_folder = folder
            print("List of csv files found:\n" + "".join([f"- {f}\n" for f in csv_files]))
            break
        except Exception as e:
            print(f"Could not access {folder}. Error: {e}")

    if not csv_files:
        print("No CSV files found. Exiting.")
    else:
        for csv_file in csv_files:
            csv_path = os.path.join(csv_folder, csv_file)
            print(f"Processing {csv_file}...")
            db_connector.update_stock_data_from_csv(csv_path)
