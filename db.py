import pandas as pd
from hdbcli import dbapi
from hana_ml import dataframe
import config
import plotly.utils
import plotly.express as px
import json

def get_connection():
    try:
        return dbapi.connect(
            address=config.HANA_HOST,
            port=int(config.HANA_PORT),
            user=config.HANA_USER,
            password=config.HANA_PASSWORD
        )
    except Exception as e:
        print(f"Failed to connect to HANA DB: {e}")
        return None

def get_hana_dataframe():
    try:
        connection_context = dataframe.ConnectionContext(
            address=config.HANA_HOST,
            port=int(config.HANA_PORT),
            user=config.HANA_USER,
            password=config.HANA_PASSWORD
        )
        hana_df = connection_context.table(
            table='Demodata',
            schema='FINANCE_DATA'
        )
        return hana_df
    except Exception as e:
        print(f"Error creating HANA DataFrame: {e}")
        return None

