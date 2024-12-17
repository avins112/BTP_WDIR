#SARIMA 

from flask import Flask, request, render_template, jsonify
import os
from ml import run_sarima_model

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/test')
def test():
    return 'test1'

@app.route('/sarima', methods=['POST'])
def sarima_forecast():
    try:
        data = request.get_json()
        gl_account = data.get('GL_ACCOUNT')
        description = data.get('DESCRIPTION')
        profit_ctr = data.get('PROFIT_CTR')
        company_code = data.get('COMPANY_CODE')

        if not all([gl_account, description, profit_ctr, company_code]):
            return jsonify({"error": "Missing input parameters"}), 400

        result = run_sarima_model(gl_account, description, profit_ctr, company_code)

        if "error" in result:
            return jsonify({"error": result["error"]}), 400

        # Include MAPE in the response
        summary = {
            "Forecast Summary": {
                "Start Date": result["dates"][0],
                "End Date": result["dates"][-1],
                "Forecast Values": [
                    {"Date": date, "Forecast": forecast, "Lower_CI": lower_ci, "Upper_CI": upper_ci}
                    for date, forecast, lower_ci, upper_ci in zip(
                        result["dates"], result["forecast"], result["lower_ci"], result["upper_ci"]
                    )
                ],
                "MAPE": result["mape"]  # Include MAPE here
            }
        }

        return jsonify(result)  # Return the result JSON
    except Exception as e:
        print(f"Error in /sarima route: {e}")
        return jsonify({"error": "Server encountered an error"}), 500


if __name__ == '__main__':
      print('hello')
      app.run(host='0.0.0.0', port=8000)
