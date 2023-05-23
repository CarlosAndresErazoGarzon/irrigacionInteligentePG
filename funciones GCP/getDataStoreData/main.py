from google.cloud import datastore
from flask import jsonify
from flask import request

def getDataStoreData(request):
    client = datastore.Client()
    query = client.query(kind = str(request.args.get('device')))
    query.order = ["-published_at"]
    results = []
    amountOfData = int(request.args.get('amount'))
    for x in query.fetch(limit= amountOfData):
        try:
            results.append(x)
        except KeyError:
            print("Error with result format, skipping entry.")

    return jsonify(message = "results", data = results)
