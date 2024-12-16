import requests
from datetime import datetime
from itertools import islice

api_key = 'X22OVHR19Z8ZBTV7'

symbol = 'IBM'


endpoint = f'https://www.alphavantage.co/query'
params = {
    'function': 'TIME_SERIES_INTRADAY',
    'symbol': symbol,
    'apikey': api_key,
    'interval':'1min',
    'adjusted':'false',
    'outputsize':'full'
}
try:
    response = requests.get(endpoint, params=params)
    data = response.json()
    daily_data = data.get('Time Series (1min)', {})
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")

except ValueError as ve:
    print(f"Error parsing response: {ve}")

#print(daily_data.items())
from pymongo import MongoClient
client = MongoClient("mongodb+srv://lakshayk:lakshayk@atria-university-data-a.uz9qe4t.mongodb.net/?retryWrites=true&w=majority")
db = client['nifty50']
collection = db['ibm_intraday']
cursor = collection.find({}).sort("date",-1).limit(1)
lastDate = ""
for document in cursor:
    lastDate = document["date"]

#print(lastDate)

if daily_data:  # Check if daily_data is not empty
    count = 0
    for key, value in daily_data.items():
        if count<5:
            if datetime.strptime(key, '%Y-%m-%d %H:%M:%S') > datetime.strptime(lastDate, '%Y-%m-%d %H:%M:%S'):
                print(f'Key: {key}, Value: {value}')
                document = {
                    "date": key,
                    "open": value['1. open'],
                    "high": value['2. high'],
                    "low": value['3. low'],
                    "close": value['4. close'],
                    "volume": value['5. volume']
                }
                result = collection.insert_one(document)
            else:
                print(f'Not submit values - Key: {key}, Value: {value}')

            count+=1
else:
    print("no daily data")



# for date, data in daily_data.items():
#     if date not in existing_dates:
#         document = {
#             "date": date,
#             "open": data['1. open'],
#             "high": data['2. high'],
#             "low": data['3. low'],
#             "close": data['4. close'],
#             "volume": data['5. volume']
#         }
#         result = collection.insert_one(document)
# client.close()