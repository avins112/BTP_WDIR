# import pandas as pd
# import matplotlib.pyplot as plt
# from pandas.tseries.offsets import MonthEnd
# from statsmodels.tsa.statespace.sarimax import SARIMAX
# from statsmodels.tools.eval_measures import rmse, meanabs

# data = df[
#     (df['GL Account'] == 600001) &
#     (df['Description'] == 'Income 1') &
#     (df['Profit Ctr'] == 'PC1') &
#     (df['Company code'] == 1000)
# ]
# data.rename(columns={'Date ': 'Date'}, inplace=True)

# # Convert Date to datetime format and set it as the index
# data['Date'] = pd.to_datetime(data['Date'], format='%Y%m') + MonthEnd(0)
# data = data.sort_values('Date')
# data.set_index('Date', inplace=True)

# # Ensure 'Amount LC' column is numeric
# time_series = pd.to_numeric(data['Amount LC'], errors='coerce')


# train_data = time_series[:'2022']
# test_data = time_series['2023':'2024']

# sarima_model = SARIMAX(train_data, order=(0, 2, 1), seasonal_order=(1, 1, 1, 12))
# fitted_sarima = sarima_model.fit(disp=False)

# # Step 4: Forecast for Test Data (Next 2 Years) and Retrieve Confidence Intervals
# forecast = fitted_sarima.get_forecast(steps=len(test_data))
# forecast_mean = forecast.predicted_mean
# forecast_ci = forecast.conf_int()

# # Step 5: Evaluate the Model on Test Data
# test_rmse = rmse(test_data, forecast_mean)
# test_mae = meanabs(test_data, forecast_mean)

# # Step 6: Plot SARIMA Predictions with Confidence Intervals
# plt.figure(figsize=(12, 6))
# plt.plot(train_data, label='Training Data', color='orange')
# plt.plot(test_data, label='Actual Test Data', color='blue')
# plt.plot(forecast_mean.index, forecast_mean, label='SARIMA Forecast', linestyle='--', color='red')
# plt.fill_between(forecast_mean.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], 
#                  color='red', alpha=0.2, label='95% Confidence Interval')
# plt.title('SARIMA Model - Forecast with Confidence Intervals')
# plt.xlabel('Date')
# plt.ylabel('Amount LC')
# plt.legend()
# plt.grid()
# plt.show()

# # Step 7: Refit Model on Full Data and Forecast Next 2 Years
# sarima_full = SARIMAX(time_series, order=(0, 2, 1), seasonal_order=(1, 1, 1, 12))
# fitted_sarima_full = sarima_full.fit(disp=False)

# # Forecast for Next 2 Years
# forecast_next_2yrs = fitted_sarima_full.get_forecast(steps=24)
# forecast_mean_next_2yrs = forecast_next_2yrs.predicted_mean
# forecast_ci_next_2yrs = forecast_next_2yrs.conf_int()

# # Plot Final Forecast with Confidence Intervals
# plt.figure(figsize=(12, 6))
# plt.plot(time_series, label='Historical Data', color='orange')
# plt.plot(forecast_mean_next_2yrs.index, forecast_mean_next_2yrs, label='SARIMA Forecast', linestyle='--', color='red')
# plt.fill_between(forecast_mean_next_2yrs.index, forecast_ci_next_2yrs.iloc[:, 0], 
#                  forecast_ci_next_2yrs.iloc[:, 1], color='red', alpha=0.2, label='95% Confidence Interval')
# plt.title('SARIMA Model - Final Forecast for Next 2 Years')
# plt.xlabel('Date')
# plt.ylabel('Amount LC')
# plt.legend()
# plt.grid()
# plt.show()

# # Step 8: Display Final Forecasted Values
# forecast_summary = pd.DataFrame({
#     'Forecast': forecast_mean_next_2yrs,
#     'Lower_CI': forecast_ci_next_2yrs.iloc[:, 0],
#     'Upper_CI': forecast_ci_next_2yrs.iloc[:, 1]
# })
# forecast_summary.reset_index(inplace=True)
# forecast_summary.rename(columns={'index': 'Date'}, inplace=True)


import pandas as pd
from pandas.tseries.offsets import MonthEnd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.eval_measures import rmse, meanabs
from db import get_hana_dataframe

def run_sarima_model(gl_account, description, profit_ctr, company_code):
    try:
        # Fetch data from HANA DB
        hana_df = get_hana_dataframe()
        if hana_df is None:
            return {"error": "Database connection failed."}

        # Collect data into a pandas DataFrame
        hana_df = hana_df.collect()
        print(hana_df.columns)
        # Validate input data
        data = hana_df[
            (hana_df['GL Account'] == int(gl_account)) &
            (hana_df['Description'] == description) &
            (hana_df['Profit Ctr'] == profit_ctr) &
            (hana_df['Company code'] == int(company_code))
        ]

        if data.empty:
            return {"error": "No matching data found for the given filters."}

        print(data.columns)
        # Preprocess Data
        data.rename(columns={'Date ': 'Date'}, inplace=True)
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce') + MonthEnd(0)
        data = data.sort_values('Date').set_index('Date')
        time_series = pd.to_numeric(data['AMOUNT_LC'], errors='coerce')

        # Train/Test Split
        train_data = time_series[:'2022']
        test_data = time_series['2023':'2024']

        # Train SARIMA Model
        sarima_model = SARIMAX(train_data, order=(0, 2, 1), seasonal_order=(1, 1, 1, 12))
        fitted_sarima = sarima_model.fit(disp=False)

        # Forecast for Test Data
        forecast = fitted_sarima.get_forecast(steps=len(test_data))
        forecast_mean = forecast.predicted_mean
        forecast_ci = forecast.conf_int()

        # Prepare JSON Response
        forecast_result = {
            "dates": list(forecast_mean.index.strftime('%Y-%m')),
            "forecast": list(forecast_mean),
            "lower_ci": list(forecast_ci.iloc[:, 0]),
            "upper_ci": list(forecast_ci.iloc[:, 1]),
        }
        return forecast_result

    except Exception as e:
        print(f"Error in SARIMA model: {e}")
        return {"error": "An error occurred during the forecasting process."}
