from pymongo import MongoClient
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler


model = load_model('model_updated.h5')

uri = "mongodb+srv://lakshayk:lakshayk@atria-university-data-a.uz9qe4t.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client.get_database("nifty50")
collection = db["ibm_intraday"]
cursor = collection.find({}).sort("date", -1).limit(1000)
unique_dates = collection.distinct("date")

data = list(cursor)
df = pd.DataFrame(data)

df['close'] = df['close'].astype(float)
scaler = MinMaxScaler()
scaler.fit(df['close'].values.reshape(-1, 1))
trainingSet = scaler.transform(df['close'].values.reshape(-1, 1))
pastDataPoints = df.shape[0]
requiredDataPoints = 60

lastActualPrices = trainingSet[-pastDataPoints:]
input_sequences = []

for i in range(len(lastActualPrices) - requiredDataPoints):
    input_sequence = lastActualPrices[i:i + requiredDataPoints]
    input_sequences.append(input_sequence)

predicted_prices = []

for input_sequence in input_sequences:
    input_sequence = np.array(input_sequence)
    input_sequence = input_sequence.reshape(1, requiredDataPoints, 1)
    val = model.predict(input_sequence)
    val = scaler.inverse_transform(val)
    predicted_prices.append(float(val[0][0]))

lastDates = df['date'][-(pastDataPoints - requiredDataPoints):]
lastDates = lastDates.tolist()
lastActualPrices = scaler.inverse_transform(np.array(lastActualPrices).reshape(-1, 1))
lastActualPrices = [price[0] for price in lastActualPrices]
print(lastDates)

for i in range(len(lastDates)):
    query = {"date":lastDates[i]}
    print(query)
    updatedData = {"$set":{"predictedValues":predicted_prices[i]}}
    result = collection.update_one(query,updatedData)
    print(result)


# from pymongo import MongoClient
#
# uri = "mongodb+srv://lakshayk:lakshayk@atria-university-data-a.uz9qe4t.mongodb.net/?retryWrites=true&w=majority"
# client = MongoClient(uri)
# db = client.get_database("nifty50")
# collection = db["ibm_intraday"]
#
# # Create a set to keep track of unique dates
# unique_dates = set()
#
# # Iterate through the cursor to find and remove duplicate documents
# for document in collection.find({}).sort("date", -1).limit(1000):
#     date = document["date"]
#
#     # Check if 'predictedValues' exists and is not empty in the document
#     if "predictedValues" not in document or not document["predictedValues"]:
#         print("Deleting document without 'predictedValues':"+str(document))
#         collection.delete_one({"date": date})
#
# # Close the MongoDB client when you're done
# client.close()
