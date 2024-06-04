import psycopg2
import pandas as pd

def fetch_data_from_postgres():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="crime_analytics",
            user="rachitagarwal",
            password="R@chit2205"
        )
        cursor = connection.cursor()
        print("Connected to database!")

        cursor.execute("SELECT * FROM crime_reports;")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        # Create a DataFrame from the fetched data
        df = pd.DataFrame(rows,columns=column_names)
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

