import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv



load_dotenv()

database_uri = os.getenv('COCKROACH_CONNECT_URI')

_cached_data = None

def fetch_data_from_postgres():
    global _cached_data
    if _cached_data is not None:
        return _cached_data

    try:
        connection = psycopg2.connect(database_uri)
        cursor = connection.cursor()
        print("Connected to database!")

        cursor.execute("SELECT * FROM crime_reports;")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        # Create a DataFrame from the fetched data
        df = pd.DataFrame(rows,columns=column_names)
        _cached_data = df
        return df  # Print the first few rows of the DataFrame
    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL", error)

    finally:
        # Close the cursor and connection
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection is not None:
            connection.close()
        print("PostgreSQL connection is closed")
