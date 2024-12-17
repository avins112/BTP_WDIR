# from flask import Flask, request, render_template, jsonify
# import os
# from db import insert_data, setup_schema_and_table, get_summary_statistics, generate_custom_plot

# app = Flask(__name__)

# UPLOAD_FOLDER = './uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route('/')
# def index():
#     return render_template('upload.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     file = request.files['file']
#     filename = file.filename
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(filepath)
    
#     setup_schema_and_table()
#     insert_data(filepath)

#     # Retrieve summary statistics
#     summary_stats = get_summary_statistics()

#     if summary_stats is not None:
#         html_data = summary_stats.to_html(classes='table table-striped', border=0, index=False)
#     else:
#         html_data = "Error retrieving summary statistics."

#     return render_template('upload.html', table_data=html_data)

# @app.route('/generate-graph', methods=['POST'])
# def generate_graph():
#     user_query = request.json  # Get user query from the frontend
#     column_x = user_query.get('x_axis')
#     column_y = user_query.get('y_axis')
#     chart_type = user_query.get('chart_type')

#     graph = generate_custom_plot(column_x, column_y, chart_type)

#     if graph:
#         return jsonify({"graph": graph})
#     else:
#         return jsonify({"error": "Unable to generate graph"}), 400

# if __name__ == '__main__':
#     app.run(debug=True)



#SARIMA 

from flask import Flask, request, render_template, jsonify
import os
from db import  get_summary_statistics, generate_custom_plot
from ml import run_sarima_model

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    setup_schema_and_table()
    insert_data(filepath)

    # Retrieve summary statistics
    summary_stats = get_summary_statistics()

    if summary_stats is not None:
        html_data = summary_stats.to_html(classes='table table-striped', border=0, index=False)
    else:
        html_data = "Error retrieving summary statistics."

    return render_template('upload.html', table_data=html_data)

@app.route('/generate-graph', methods=['POST'])
def generate_graph():
    user_query = request.json  # Get user query from the frontend
    column_x = user_query.get('x_axis')
    column_y = user_query.get('y_axis')
    chart_type = user_query.get('chart_type')

    graph = generate_custom_plot(column_x, column_y, chart_type)

    if graph:
        return jsonify({"graph": graph})
    else:
        return jsonify({"error": "Unable to generate graph"}), 400

@app.route('/sarima', methods=['POST'])
def sarima_forecast():
    try:
        data = request.get_json()  # Get JSON data from the request
        gl_account = data.get('GL_ACCOUNT')
        description = data.get('DESCRIPTION')
        profit_ctr = data.get('PROFIT_CTR')
        company_code = data.get('COMPANY_CODE')

        # Validate input
        if not all([gl_account, description, profit_ctr, company_code]):
            return jsonify({"error": "Missing input parameters"}), 400

        # Run SARIMA model
        result = run_sarima_model(gl_account, description, profit_ctr, company_code)

        if "error" in result:
            return jsonify({"error": result["error"]}), 400
        return jsonify(result)
    except Exception as e:
        print(f"Error in /sarima route: {e}")
        return jsonify({"error": "Server encountered an error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
