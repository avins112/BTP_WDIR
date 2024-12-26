from flask import Flask, request, render_template, jsonify
from joblib import load
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import json
import plotly

# Initialize Flask app
app = Flask(__name__)

# Load the input data
data = pd.read_csv("resampled.csv")
data = data[['date', 'demand']].rename(columns={"date": "SETTLEMENTDATE", "demand": "TOTALDEMAND"})
data['SETTLEMENTDATE'] = pd.to_datetime(data['SETTLEMENTDATE'])

# Load the pre-trained model
model = load("forecasting_model.joblib")


@app.route('/')
def home():
    # Serve the HTML form for input
    return render_template('index.html')


@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        # Get horizon value from the form
        horizon = int(request.form['horizon'])

        # Forecast for the given horizon
        future_df = model.forecast(iInputDS=data, iHorizon=horizon)

        # Extract forecasted data
        forecasted_demand = future_df[['SETTLEMENTDATE', 'TOTALDEMAND_Forecast']].tail(horizon)
        forecast_df = future_df[['SETTLEMENTDATE', 'TOTALDEMAND_Forecast']]

        # Add weekly and monthly aggregations
        forecast_df['Week'] = forecast_df['SETTLEMENTDATE'].dt.to_period('W').astype(str)  # Weekly buckets
        forecast_df['Month'] = forecast_df['SETTLEMENTDATE'].dt.to_period('M').astype(str)  # Monthly buckets

        # Create a Plotly figure
        fig = make_subplots(rows=1, cols=1)

        # Historical data
        fig.add_trace(go.Scatter(
            x=data['SETTLEMENTDATE'],
            y=data['TOTALDEMAND'],
            mode='lines',
            name='Historical Demand',
            line=dict(color='blue')
        ))

        # Forecasted data (Daily)
        fig.add_trace(go.Scatter(
            x=forecast_df['SETTLEMENTDATE'],
            y=forecast_df['TOTALDEMAND_Forecast'],
            mode='lines+markers',
            name='Forecasted Demand (Daily)',
            line=dict(color='orange', dash='dot')
        ))

        # Weekly Aggregation
        weekly_forecast = forecast_df.groupby('Week').mean().reset_index()
        fig.add_trace(go.Scatter(
            x=weekly_forecast['Week'],
            y=weekly_forecast['TOTALDEMAND_Forecast'],
            mode='lines+markers',
            name='Forecasted Demand (Weekly)',
            line=dict(color='purple')
        ))

        # Monthly Aggregation
        monthly_forecast = forecast_df.groupby('Month').mean().reset_index()
        fig.add_trace(go.Scatter(
            x=monthly_forecast['Month'],
            y=monthly_forecast['TOTALDEMAND_Forecast'],
            mode='lines+markers',
            name='Forecasted Demand (Monthly)',
            line=dict(color='green')
        ))

        # Add vertical line for forecast start
        fig.add_shape(type="line",
                      x0=data['SETTLEMENTDATE'].iloc[-1], x1=data['SETTLEMENTDATE'].iloc[-1],
                      y0=min(data['TOTALDEMAND']), y1=max(data['TOTALDEMAND']),
                      line=dict(color="red", dash="dot"),
                      name='Forecast Start')

        # Layout configurations
        fig.update_layout(
            title="Electricity Demand Forecast (Interactive)",
            xaxis_title="Date",
            yaxis_title="Total Demand",
            legend=dict(x=0, y=1),
            hovermode="x"
        )

        # Convert the plot to JSON for rendering in the frontend
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Return the forecast and visualization as JSON
        return render_template('index.html', forecast=forecasted_demand.to_dict(orient="records"), plot=plot_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
