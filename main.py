import json
from datetime import datetime, timedelta
from flask import Flask, render_template
from pymongo import MongoClient
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from flask_cors import CORS


model = load_model('model.h5')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5000/stock_chart_api"])
app.config['DEBUG'] = True

uri = "mongodb+srv://lakshayk:lakshayk@atria-university-data-a.uz9qe4t.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client.get_database("nifty50")
collection = db["ibm_intraday"]
cursor = collection.find({}).sort("date", 1).limit(60)
data = list(cursor)
df = pd.DataFrame(data)




df['close'] = df['close'].astype(float)
scaler = MinMaxScaler()
scaler.fit(df['close'].values.reshape(-1, 1))
trainingSet = scaler.transform(df['close'].values.reshape(-1, 1))
pastDataPoints = df.shape[0]
requiredDataPoints = 60


@app.route('/stock_chart_api')
def stock_chart_api():
    uri = "mongodb+srv://lakshayk:lakshayk@atria-university-data-a.uz9qe4t.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client.get_database("nifty50")
    collection = db["ibm_intraday"]
    cursor = collection.find({"predictedValues": {"$exists": True}}).sort("date", - 1).limit(250)
    all_documents = list(collection.find({"predictedValues": {"$exists": True}}).sort("date", -1).limit(250))
    first_document = all_documents[0]
    last_document = all_documents[-1]
    print(first_document," \n ",last_document)
    actualValues = []
    predictedValues = []
    actualDateTime = []

    for document in cursor:
        actualValues.append(float(document['close']))  # Convert to float
        predictedValues.append(document['predictedValues'])
        actualDateTime.append(datetime.strptime(document['date'], '%Y-%m-%d %H:%M:%S'))

    print(actualValues, "\n", predictedValues, "\n", actualDateTime)
    print(len(actualValues), "\n", len(predictedValues), "\n", len(actualDateTime))
    actualDateTime = actualDateTime
    lastTime = actualDateTime[0]
    print(actualDateTime[:5])
    targetTime = lastTime + timedelta(minutes=1)
    print(lastTime)
    trainingPoints = actualValues[-60:]
    trainingPoints = np.array(trainingPoints)
    trainingPoints = scaler.transform(trainingPoints.reshape(-1, 1))
    trainingPoints = trainingPoints.reshape(1, requiredDataPoints, 1)
    outp = model.predict(trainingPoints)
    outp = scaler.inverse_transform(outp)
    outp = outp.reshape(-1, 1)
    outp = outp[0][0]
    print(outp)

    result = {
        "nextMinuteData": str(outp),
        "targetTime": str(targetTime),
        "actualData": actualValues,  # Use the list of float values
        "predictedData": predictedValues,
        "actualDateTime": [str(dt) for dt in actualDateTime]  # Format dates as strings
    }
    jsonOutput = json.dumps(result)
    return jsonOutput

@app.route("/")
def show_chart():
    return render_template("chart.html")
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
