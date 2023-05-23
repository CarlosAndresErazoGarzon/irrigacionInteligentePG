from google.cloud import datastore
from flask import jsonify

def read_datastore_data(request):
    client, kinds, results = datastore.Client(), ["SYS01_1", "SYS02_1"], []
    
    for kind in kinds:
        query, query.order = client.query(kind = kind), ["-published_at"]
         
        for data in query.fetch(limit = 1):
            try:
                results.append(data)
            except KeyError:
                print("Error with result format, skipping entry.")

    return jsonify(message = "results", data = results)