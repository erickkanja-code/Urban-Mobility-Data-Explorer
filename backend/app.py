from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/trips', methods=['GET'])
def get_trips():
    df = pd.read_csv('data/clean_trips_features.csv')
    return jsonify(df.head(100).to_dict(orient='records'))  # return first 100 for demo

if __name__ == "__main__":
    app.run(debug=True)
