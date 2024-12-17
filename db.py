# import pandas as pd
# from hdbcli import dbapi
# from hana_ml import dataframe
# import config
# import plotly.utils
# import plotly.express as px
# import json

# def get_connection():
#     try:
#         return dbapi.connect(
#             address=config.HANA_HOST,
#             port=int(config.HANA_PORT),
#             user=config.HANA_USER,
#             password=config.HANA_PASSWORD
#         )
#     except Exception as e:
#         print(f"Failed to connect to HANA DB: {e}")
#         return None

# def get_hana_dataframe():
#     try:
#         connection_context = dataframe.ConnectionContext(
#             address=config.HANA_HOST,
#             port=int(config.HANA_PORT),
#             user=config.HANA_USER,
#             password=config.HANA_PASSWORD
#         )
#         hana_df = connection_context.table(
#             table='Demodata',
#             schema='FINANCE_DATA'
#         )
#         return hana_df
#     except Exception as e:
#         print(f"Error creating HANA DataFrame: {e}")
#         return None


import pandas as pd
from hdbcli import dbapi
from hana_ml import dataframe
import config
import plotly.express as px
import json

def get_connection():
    """
    Establishes a connection to SAP HANA using hdbcli with SSL certificate.
    """
    try:
        connection = dbapi.connect(
            address=config.HANA_HOST,
            port=int(config.HANA_PORT),
            user=config.HANA_USER,
            encrypt='true',
            password=config.HANA_PASSWORD,
            sslTrustStore=config.HANA_CERTIFICATE
        )
        print("Successfully connected to SAP HANA (hdbcli)")
        return connection
    except Exception as e:
        print(f"Failed to connect to HANA DB using hdbcli: {e}")
        return None

def get_hana_dataframe():
    """
    Creates a HANA ML DataFrame using hana_ml.ConnectionContext with SSL configuration.
    """
    try:
        connection_context = dataframe.ConnectionContext(
            address=config.HANA_HOST,
            port=int(config.HANA_PORT),
            user=config.HANA_USER,
            password=config.HANA_PASSWORD,
            encrypt='true',
            sslTrustStore=config.HANA_CERTIFICATE
        )
        print("Successfully connected to SAP HANA (hana_ml)")

        # Replace table and schema as needed
        hana_df = connection_context.table(
            table='"ForecastData"',  # Table name is case-sensitive, quoted
            schema='my_data'
        )
        print("HANA DataFrame loaded successfully.")
        return hana_df
    except Exception as e:
        print(f"Error creating HANA DataFrame: {e}")
        return None

def main():
    """
    Main function to test both the DBAPI connection and hana_ml DataFrame.
    """
    print("\n=== Testing SAP HANA Connections ===")

    # Test HDBCLI Connection
    connection = get_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM \"my_data\".\"ForecastData\"")
            result = cursor.fetchone()
            print(f"Row count using hdbcli: {result[0]}")
            cursor.close()
        except Exception as e:
            print(f"Error running query via hdbcli: {e}")
        finally:
            connection.close()
            print("HDBCLI connection closed.\n")

    # Test hana_ml DataFrame
    hana_df = get_hana_dataframe()
    if hana_df is not None:
        try:
            pandas_df = hana_df.collect()  # Convert HANA ML DataFrame to pandas DataFrame
            print(f"Data loaded via hana_ml (first 5 rows):\n{pandas_df.head()}")
            
            # Example Visualization using Plotly
            print("Generating sample chart...")
            fig = px.line(pandas_df, x='date', y='forecast', title='Forecast Data Visualization')
            fig.show()
        except Exception as e:
            print(f"Error processing HANA ML DataFrame: {e}")

if __name__ == "__main__":
    main()

