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

# def setup_schema_and_table():
#     conn = get_connection()
#     if conn:
#         cursor = conn.cursor()
#         try:
#             cursor.execute("SELECT SCHEMA_NAME FROM SCHEMAS WHERE SCHEMA_NAME = 'FINANCE_DATA'")
#             if not cursor.fetchone():
#                 cursor.execute("CREATE SCHEMA FINANCE_DATA")
#             cursor.execute("SELECT COUNT(*) FROM TABLES WHERE SCHEMA_NAME = 'FINANCE_DATA' AND TABLE_NAME = 'FINANCIAL_DATA'")
#             if cursor.fetchone()[0] == 0:
#                 cursor.execute("""
#                     CREATE TABLE FINANCE_DATA.FINANCIAL_DATA (
#                         "DATE" DATE,
#                         "COMPANY_CODE" INT,
#                         "GL_ACCOUNT" INT,
#                         "DESCRIPTION" VARCHAR(255),
#                         "LOCATION" VARCHAR(100),
#                         "PROFIT_CTR" VARCHAR(50),
#                         "COST_CTR" VARCHAR(50),
#                         "AUDIT_TRAIL" VARCHAR(50),
#                         "AMOUNT_LC" DECIMAL(18, 2)
#                     )
#                 """)
#             conn.commit()
#         except dbapi.Error as e:
#             print(f"Error creating schema/table: {e}")
#         finally:
#             cursor.close()
#             conn.close()
#     else:
#         print("Unable to proceed without a database connection.")

# def get_database_column_names():
#     conn = get_connection()
#     if conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT COLUMN_NAME FROM TABLE_COLUMNS WHERE SCHEMA_NAME = 'FINANCE_DATA' AND TABLE_NAME = 'FINANCIAL_DATA'")
#         columns = [row[0] for row in cursor.fetchall()]
#         cursor.close()
#         conn.close()
#         return columns
#     return []

# def clean_column_names(df, db_columns):
#     df.columns = [col.strip().replace(" ", "_").replace("-", "_").upper() for col in df.columns]
#     df.columns = [col if col in db_columns else None for col in df.columns]
#     df = df.loc[:, df.columns.notnull()]
#     return df

# def format_date_column(df):
#     if 'DATE' in df.columns:
#         df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.strftime('%Y-%m-%d')
#     return df

# def insert_data(file_path):
#     db_columns = get_database_column_names()
#     df = pd.read_excel(file_path)
#     df = clean_column_names(df, db_columns)
#     df = format_date_column(df)
#     conn = get_connection()
#     if conn:
#         cursor = conn.cursor()
#         try:
#             columns = ', '.join([f'"{col}"' for col in df.columns if col in db_columns])
#             placeholders = ', '.join(['?'] * len(df.columns))
#             sql = f"INSERT INTO FINANCE_DATA.FINANCIAL_DATA ({columns}) VALUES ({placeholders})"
#             for index, row in df.iterrows():
#                 cursor.execute(sql, tuple(row))
#             conn.commit()
#         except Exception as e:
#             print(f"Error inserting data: {e}")
#         finally:
#             cursor.close()
#             conn.close()
#     else:
#         print("Failed to connect to the database.")

# def get_hana_dataframe():
#     try:
#         connection_context = dataframe.ConnectionContext(
#             address=config.HANA_HOST,
#             port=int(config.HANA_PORT),
#             user=config.HANA_USER,
#             password=config.HANA_PASSWORD
#         )
#         hana_df = connection_context.table(
#             table='FINANCIAL_DATA',
#             schema='FINANCE_DATA'
#         )
#         return hana_df
#     except Exception as e:
#         print(f"Error creating HANA DataFrame: {e}")
#         return None

# def get_summary_statistics():
#     hana_df = get_hana_dataframe()
#     if hana_df is not None:
#         try:
#             desc = hana_df.describe()
#             return desc.collect()
#         except Exception as e:
#             print(f"Error computing summary statistics: {e}")
#             return None
#     else:
#         print("HANA DataFrame is not available.")
#         return None


# def generate_plots(summary_stats):
#     graphs = []
#     try:
#         # Bar chart for unique counts
#         if 'column' in summary_stats.columns and 'unique' in summary_stats.columns:
#             fig = px.bar(
#                 summary_stats,
#                 x='column',
#                 y='unique',
#                 title="Unique Count per Column",
#                 labels={"unique": "Unique Count"}
#             )
#             graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

#         # Scatter plot for min vs max
#         if 'min' in summary_stats.columns and 'max' in summary_stats.columns:
#             fig = px.scatter(
#                 summary_stats,
#                 x='min',
#                 y='max',
#                 title="Min vs Max Values",
#                 labels={"min": "Min Value", "max": "Max Value"}
#             )
#             graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

#         # Print for debugging
#         print("Generated Graphs:", graphs)

#     except Exception as e:
#         print(f"Error generating plots: {e}")
#     return graphs



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

def setup_schema_and_table():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT SCHEMA_NAME FROM SCHEMAS WHERE SCHEMA_NAME = 'FINANCE_DATA'")
            if not cursor.fetchone():
                cursor.execute("CREATE SCHEMA FINANCE_DATA")
            cursor.execute("SELECT COUNT(*) FROM TABLES WHERE SCHEMA_NAME = 'FINANCE_DATA' AND TABLE_NAME = 'FINANCIAL_DATA'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    CREATE TABLE FINANCE_DATA.FINANCIAL_DATA (
                        "DATE" DATE,
                        "COMPANY_CODE" INT,
                        "GL_ACCOUNT" INT,
                        "DESCRIPTION" VARCHAR(255),
                        "LOCATION" VARCHAR(100),
                        "PROFIT_CTR" VARCHAR(50),
                        "COST_CTR" VARCHAR(50),
                        "AUDIT_TRAIL" VARCHAR(50),
                        "AMOUNT_LC" DECIMAL(18, 2)
                    )
                """)
            conn.commit()
        except dbapi.Error as e:
            print(f"Error creating schema/table: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Unable to proceed without a database connection.")

def get_database_column_names():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COLUMN_NAME FROM TABLE_COLUMNS WHERE SCHEMA_NAME = 'FINANCE_DATA' AND TABLE_NAME = 'FINANCIAL_DATA'")
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return columns
    return []

def clean_column_names(df, db_columns):
    df.columns = [col.strip().replace(" ", "_").replace("-", "_").upper() for col in df.columns]
    df.columns = [col if col in db_columns else None for col in df.columns]
    df = df.loc[:, df.columns.notnull()]
    return df

def format_date_column(df):
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

def insert_data(file_path):
    db_columns = get_database_column_names()
    df = pd.read_excel(file_path)
    df = clean_column_names(df, db_columns)
    df = format_date_column(df)
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            columns = ', '.join([f'"{col}"' for col in df.columns if col in db_columns])
            placeholders = ', '.join(['?'] * len(df.columns))
            sql = f"INSERT INTO FINANCE_DATA.FINANCIAL_DATA ({columns}) VALUES ({placeholders})"
            for index, row in df.iterrows():
                cursor.execute(sql, tuple(row))
            conn.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Failed to connect to the database.")

def get_hana_dataframe():
    try:
        connection_context = dataframe.ConnectionContext(
            address=config.HANA_HOST,
            port=int(config.HANA_PORT),
            user=config.HANA_USER,
            password=config.HANA_PASSWORD
        )
        hana_df = connection_context.table(
            table='FINANCIAL_DATA',
            schema='FINANCE_DATA'
        )
        return hana_df
    except Exception as e:
        print(f"Error creating HANA DataFrame: {e}")
        return None

def get_summary_statistics():
    hana_df = get_hana_dataframe()
    if hana_df is not None:
        try:
            desc = hana_df.describe()
            return desc.collect()
        except Exception as e:
            print(f"Error computing summary statistics: {e}")
            return None
    else:
        print("HANA DataFrame is not available.")
        return None

def generate_plots(summary_stats):
    graphs = []
    try:
        if 'column' in summary_stats.columns and 'unique' in summary_stats.columns:
            fig = px.bar(
                summary_stats,
                x='column',
                y='unique',
                title="Unique Count per Column",
                labels={"unique": "Unique Count"}
            )
            graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

        if 'min' in summary_stats.columns and 'max' in summary_stats.columns:
            fig = px.scatter(
                summary_stats,
                x='min',
                y='max',
                title="Min vs Max Values",
                labels={"min": "Min Value", "max": "Max Value"}
            )
            graphs.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

        print("Generated Graphs:", graphs)

    except Exception as e:
        print(f"Error generating plots: {e}")
    return graphs

def generate_custom_plot(x_axis, y_axis, chart_type):
    hana_df = get_hana_dataframe()

    if hana_df is not None:
        try:
            data = hana_df.collect()

            if chart_type == 'bar':
                fig = px.bar(data, x=x_axis, y=y_axis, title=f"{chart_type.capitalize()} Chart")
            elif chart_type == 'scatter':
                fig = px.scatter(data, x=x_axis, y=y_axis, title=f"{chart_type.capitalize()} Chart")
            elif chart_type == 'line':
                fig = px.line(data, x=x_axis, y=y_axis, title=f"{chart_type.capitalize()} Chart")
            else:
                return None

            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        except Exception as e:
            print(f"Error generating custom plot: {e}")
            return None
    else:
        print("HANA DataFrame is not available.")
        return None
