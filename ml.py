# import pandas as pd
# from pandas.tseries.offsets import MonthEnd
# from statsmodels.tsa.statespace.sarimax import SARIMAX
# from statsmodels.tools.eval_measures import rmse, meanabs
# import matplotlib.pyplot as plt
# import base64
# from io import BytesIO
# from pandas.tseries.offsets import MonthEnd
# from statsmodels.tsa.statespace.sarimax import SARIMAX
# import pandas as pd

# def run_sarima_model(gl_account, description, profit_ctr, company_code):
#     try:
#         # Fetch data from HANA DB
#         hana_df = get_hana_dataframe()
#         if hana_df is None:
#             return {"error": "Database connection failed."}

#         # Collect data into a pandas DataFrame
#         hana_df = hana_df.collect()
        
#         # Validate input data
#         data = hana_df[
#             (hana_df['GL Account'] == gl_account) &
#             (hana_df['Description'] == description) &
#             (hana_df['Profit Ctr'] == profit_ctr) &
#             (hana_df['Company code'] == company_code)
#         ]
#         if data.empty:
#             return {"error": "No matching data found for the given filters."}

#         data.rename(columns={'Date ': 'Date'}, inplace=True)
#         # Convert Date to datetime format and set it as the index
#         data['Date'] = pd.to_datetime(data['Date'], format='%Y%m') + MonthEnd(0)
#         data = data.sort_values('Date')
#         data.set_index('Date', inplace=True)
    
#         # Convert Amount LC to numeric
#         time_series = pd.to_numeric(data['Amount LC'], errors='coerce').dropna()

#         # Check if index is monotonic
#         if not time_series.index.is_monotonic_increasing:
#             time_series = time_series.sort_index()

#         # Train/Test Split
#         train_data = time_series[:'2024']
#         sarima_full = SARIMAX(time_series, order=(0, 2, 1), seasonal_order=(1, 1, 1, 12))
#         fitted_sarima_full = sarima_full.fit(disp=False)

#         # Forecast for Next 2 Years
#         forecast_next_2yrs = fitted_sarima_full.get_forecast(steps=24)
#         forecast_mean_next_2yrs = forecast_next_2yrs.predicted_mean
#         forecast_ci_next_2yrs = forecast_next_2yrs.conf_int()

#         # Generate Graph
#         plt.figure(figsize=(10, 6))
#         plt.plot(train_data, label='Train Data', color='blue')
#         plt.plot(forecast_mean_next_2yrs, label='Forecast', color='red', linestyle='--')
#         plt.fill_between(forecast_ci_next_2yrs.index, forecast_ci_next_2yrs.iloc[:, 0], forecast_ci_next_2yrs.iloc[:, 1],
#                          color='red', alpha=0.2, label='Confidence Interval')
#         plt.legend()
#         plt.title('SARIMA Forecast')
#         plt.xlabel('Date')
#         plt.ylabel('Amount LC')
#         plt.grid()

#         # Save Plot to Base64
#         buffer = BytesIO()
#         plt.savefig(buffer, format='png')
#         buffer.seek(0)
#         plot_image = base64.b64encode(buffer.read()).decode('utf-8')
#         plt.close()

#         forcast =  {
#             "dates": list(forecast_mean_next_2yrs.index.strftime('%Y-%m')),
#             "forecast": list(forecast_mean_next_2yrs),
#             "lower_ci": list(forecast_ci_next_2yrs.iloc[:, 0]),
#             "upper_ci": list(forecast_ci_next_2yrs.iloc[:, 1]),
#             "plot": plot_image
#         }
#         return forcast
#     except Exception as e:
#         print(f"Error in SARIMA model: {e}")
#         return {"error": str(e)}

from db import get_hana_dataframe
# import pandas as pd
# import matplotlib.pyplot as plt
# from pandas.tseries.offsets import MonthEnd
# from statsmodels.tsa.statespace.sarimax import SARIMAX
# import itertools
# import base64
# from io import BytesIO

# # Function to calculate MAPE
# def mean_absolute_percentage_error(y_true, y_pred):
#     return (abs((y_true - y_pred) / y_true).mean()) * 100

# def run_sarima_model(gl_account, description, profit_ctr, company_code):
#     try:
#         # Fetch data from HANA DB
#         hana_df = get_hana_dataframe()
#         if hana_df is None:
#             return {"error": "Database connection failed."}

#         # Collect data into a pandas DataFrame
#         hana_df = hana_df.collect()

#         # Filter data based on input parameters
#         data = hana_df[
#             (hana_df['GL Account'] == gl_account) &
#             (hana_df['Description'] == description) &
#             (hana_df['Profit Ctr'] == profit_ctr) &
#             (hana_df['Company code'] == company_code)
#         ]
#         if data.empty:
#             return {"error": "No matching data found for the given filters."}

#         data.rename(columns={'Date ': 'Date'}, inplace=True)
#         data['Date'] = pd.to_datetime(data['Date'], format='%Y%m') + MonthEnd(0)
#         data = data.sort_values('Date')
#         data.set_index('Date', inplace=True)
#         time_series = pd.to_numeric(data['Amount LC'], errors='coerce').dropna()

#         # Check if index is monotonic
#         if not time_series.index.is_monotonic_increasing:
#             time_series = time_series.sort_index()

#         # Step 1: Train-Test Split
#         train_data = time_series[:'2023']
#         test_data = time_series['2024']

#         # Step 2: Grid Search to Minimize Average Expected MAPE
#         p = d = q = range(0, 3)  # Regular ARIMA parameters
#         P = D = Q = range(0, 2)  # Seasonal parameters
#         m = 12  # Seasonality (12 months for yearly patterns)

#         param_combinations = list(itertools.product(p, d, q, P, D, Q))
#         best_mape = float("inf")
#         best_params = None
#         best_model = None

#         for params in param_combinations:
#             try:
#                 p, d, q, P, D, Q = params
#                 seasonal_order = (P, D, Q, m)
#                 model = SARIMAX(train_data, order=(p, d, q), seasonal_order=seasonal_order)
#                 fitted_model = model.fit(disp=False)

#                 forecast = fitted_model.get_forecast(steps=len(test_data))
#                 forecast_mean = forecast.predicted_mean

#                 mape = mean_absolute_percentage_error(test_data, forecast_mean)
#                 if mape < best_mape:
#                     best_mape = mape
#                     best_params = (p, d, q, P, D, Q)
#                     best_model = fitted_model
#             except Exception as e:
#                 continue

#         if best_model is None:
#             return {"error": "No valid SARIMA model was found."}

#         print(f"Best SARIMA Parameters: {best_params}")
#         print(f"Best Average Expected MAPE on Test Data (2024): {best_mape:.2f}%")

#         # Step 3: Forecast for Next 2 Years (2025-2026)
#         forecast_steps = 24
#         forecast_next_2yrs = best_model.get_forecast(steps=forecast_steps)
#         forecast_mean_next_2yrs = forecast_next_2yrs.predicted_mean
#         forecast_ci_next_2yrs = forecast_next_2yrs.conf_int()

#         # Adjust forecast index
#         forecast_mean_next_2yrs.index = pd.date_range(start='2025-01-31', periods=forecast_steps, freq='M')
#         forecast_ci_next_2yrs.index = forecast_mean_next_2yrs.index

#         # Generate Graph
#         plt.figure(figsize=(10, 6))
#         plt.plot(train_data, label='Train Data', color='blue')
#         plt.plot(forecast_mean_next_2yrs, label='Forecast', color='red', linestyle='--')
#         plt.fill_between(forecast_ci_next_2yrs.index, forecast_ci_next_2yrs.iloc[:, 0], forecast_ci_next_2yrs.iloc[:, 1],
#                          color='red', alpha=0.2, label='Confidence Interval')
#         plt.legend()
#         plt.title(f'SARIMA Forecast - MAPE: {best_mape:.2f}%')
#         plt.xlabel('Date')
#         plt.ylabel('Amount LC')
#         plt.grid()
#         # Save Plot to Base64
#         buffer = BytesIO()
#         plt.savefig(buffer, format='png')
#         buffer.seek(0)
#         plot_image = base64.b64encode(buffer.read()).decode('utf-8')
#         plt.close()
#         # Return Forecast and MAPE
#         forecast_summary = {
#             "dates": list(forecast_mean_next_2yrs.index.strftime('%Y-%m')),
#             "forecast": list(forecast_mean_next_2yrs),
#             "lower_ci": list(forecast_ci_next_2yrs.iloc[:, 0]),
#             "upper_ci": list(forecast_ci_next_2yrs.iloc[:, 1]),
#             "mape": best_mape,
#             "plot": plot_image
#         }
#         print(forecast_summary)
#         return forecast_summary

#     except Exception as e:
#         print(f"Error in SARIMA model: {e}")
#         return {"error": str(e)}


import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import MonthEnd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import itertools
import base64
from io import BytesIO

# Function to calculate MAPE
def mean_absolute_percentage_error(y_true, y_pred):
    return (abs((y_true - y_pred) / y_true).mean()) * 100

def run_sarima_model(gl_account, description, profit_ctr, company_code):
    try:
        # Fetch data from HANA DB
        hana_df = get_hana_dataframe()
        if hana_df is None:
            return {"error": "Database connection failed."}

        # Collect data into a pandas DataFrame
        hana_df = hana_df.collect()

        # Filter data based on input parameters
        data = hana_df[
            (hana_df['GL Account'] == gl_account) &
            (hana_df['Description'] == description) &
            (hana_df['Profit Ctr'] == profit_ctr) &
            (hana_df['Company code'] == company_code)
        ]
        if data.empty:
            return {"error": "No matching data found for the given filters."}

        data.rename(columns={'Date ': 'Date'}, inplace=True)
        data['Date'] = pd.to_datetime(data['Date'], format='%Y%m') + MonthEnd(0)
        data = data.sort_values('Date')
        data.set_index('Date', inplace=True)
        time_series = pd.to_numeric(data['Amount LC'], errors='coerce').dropna()

        # Check if index is monotonic
        if not time_series.index.is_monotonic_increasing:
            time_series = time_series.sort_index()

        # Step 1: Train-Test Split
        train_data = time_series[:'2023']
        test_data = time_series['2024']

        # Step 2: Grid Search to Minimize MAPE
        p = d = q = range(0, 3)  # Regular ARIMA parameters
        P = D = Q = range(0, 2)  # Seasonal parameters
        m = 12  # Seasonality (12 months for yearly patterns)

        param_combinations = list(itertools.product(p, d, q, P, D, Q))
        best_mape = float("inf")
        best_params = None
        best_model = None

        for params in param_combinations:
            try:
                p, d, q, P, D, Q = params
                seasonal_order = (P, D, Q, m)
                model = SARIMAX(train_data, order=(p, d, q), seasonal_order=seasonal_order)
                fitted_model = model.fit(disp=False)

                forecast = fitted_model.get_forecast(steps=len(test_data))
                forecast_mean = forecast.predicted_mean

                mape = mean_absolute_percentage_error(test_data, forecast_mean)
                if mape < best_mape:
                    best_mape = mape
                    best_params = (p, d, q, P, D, Q)
                    best_model = fitted_model
            except Exception as e:
                continue

        if best_model is None:
            return {"error": "No valid SARIMA model was found."}

        print(f"Best SARIMA Parameters: {best_params}")
        print(f"Best MAPE on Test Data (2024): {best_mape:.2f}%")

        # Step 3: Forecast for Next 2 Years (2025-2026)
        forecast_steps = 24
        forecast_next_2yrs = best_model.get_forecast(steps=forecast_steps)
        forecast_mean_next_2yrs = forecast_next_2yrs.predicted_mean
        forecast_ci_next_2yrs = forecast_next_2yrs.conf_int()

        # Adjust forecast index
        forecast_mean_next_2yrs.index = pd.date_range(start='2025-01-31', periods=forecast_steps, freq='M')
        forecast_ci_next_2yrs.index = forecast_mean_next_2yrs.index

        # Step 4: Generate Graph
        plt.figure(figsize=(12, 6))

        # Plot Train Data
        plt.plot(train_data, label='Train Data', color='blue')

        # Plot Test Data
        plt.plot(test_data, label='Test Data', color='green')

        # Plot Forecast
        plt.plot(forecast_mean_next_2yrs, label='Forecast', color='red', linestyle='--')

        # Plot Confidence Interval
        plt.fill_between(forecast_ci_next_2yrs.index, forecast_ci_next_2yrs.iloc[:, 0],
                         forecast_ci_next_2yrs.iloc[:, 1], color='red', alpha=0.2, label='Confidence Interval')

        # Add Labels and Title
        plt.legend()
        plt.title(f'SARIMA Forecast - MAPE: {best_mape:.2f}%')
        plt.xlabel('Date')
        plt.ylabel('Amount LC')
        plt.grid()

        # Save Plot to Base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_image = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        # Step 5: Return Forecast and MAPE
        forecast_summary = {
            "dates": list(forecast_mean_next_2yrs.index.strftime('%Y-%m')),
            "forecast": list(forecast_mean_next_2yrs),
            "lower_ci": list(forecast_ci_next_2yrs.iloc[:, 0]),
            "upper_ci": list(forecast_ci_next_2yrs.iloc[:, 1]),
            "mape": best_mape,
            "plot": plot_image
        }
        print(forecast_summary)
        return forecast_summary

    except Exception as e:
        print(f"Error in SARIMA model: {e}")
        return {"error": str(e)}
