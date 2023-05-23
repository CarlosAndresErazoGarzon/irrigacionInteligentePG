from flask import Flask, jsonify
from google.cloud import datastore, storage
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from time import sleep
import datetime, os, json, numpy, pickle, requests, io, h5py, pandas

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "irrigation1-5e8a358a317c.json"
app = Flask(__name__)

@app.route("/")
def init_page():
    return "<p>Working!</p>"

#Esta función es la que está subida en Google Cloud Platform y se llama en la línea 46
@app.route("/DataStore/read")
def read_datastore_data():
    client, kinds, results = datastore.Client(), ["SYS02_1"], []
    
    for kind in kinds:
        query, query.order = client.query(kind = kind), ["-published_at"]
         
        for data in query.fetch():
            try:
                results.append(data)
            except KeyError:
                print("Error with result format, skipping entry.")

    return jsonify(message = "results", data = results)

@app.route("/DataStore/save_to_CSV")
def data_store_save_csv():
    data  = read_datastore_data().json
    data = pandas.DataFrame(data['data'])
    data.to_csv('SYS01_1_and_SYS02_1.csv', index=False)
    
    return "Saved!"

@app.route("/neural_network")
def make_prediction():
    #sleep(120)

    storage_client, datastore_client  = storage.Client(), datastore.Client(), 
    bucket = storage_client.get_bucket("neural_network_irrigation_javeriana")
    nn_blob, X_blob, y_blob = bucket.blob("neural_network.h5"), bucket.blob("X.pkl"), bucket.blob("y.pkl")
    nn_blob_contents = io.BytesIO(nn_blob.download_as_bytes())

    with h5py.File(nn_blob_contents, 'r') as h5_file:
        loaded_model = load_model(h5_file)  
          
    with X_blob.open('rb') as f:
        X  = pickle.load(f)
    
    with y_blob.open('rb') as f:
        y  = pickle.load(f)  
        
    response  = requests.get("https://us-central1-irrigation1.cloudfunctions.net/readDataStoreData")
    data = json.loads(response.text)
    data, temp_01, hum_01, lux_01, hygro_01, finalValues = data['data'], numpy.array([]), numpy.array([]), numpy.array([]), numpy.array([]), []
    scaler_X, scaler_y = MinMaxScaler(), MinMaxScaler()
    
    for value in data:
        temp_01_mean = numpy.array(value['temp_01']).mean()
        temp_02_mean = numpy.array(value['temp_02']).mean()
        hum_01_mean = numpy.array(value['hum_01']).mean()
        hum_02_mean = numpy.array(value['hum_02']).mean()
        
        if (temp_01_mean < 15 or temp_01_mean > 30) and (temp_02_mean > 0):
            temp_01 = numpy.append(temp_01, temp_02_mean)
        else: 
            temp_01 = numpy.append(temp_01, temp_01_mean)
            
        if (hum_01_mean < 60 or hum_01_mean > 105) and (hum_02_mean > 0):
            hum_01 = numpy.append(hum_01, hum_02_mean)
        else: 
            hum_01 = numpy.append(hum_01, hum_01_mean)
            
        lux_01 = numpy.append(lux_01, numpy.array(value['lux_01']).mean())
        hygro_01 = numpy.append(hygro_01, numpy.array(value['hygro_01']).mean())
        
    finalValues = [val for tup in zip(temp_01, hum_01, lux_01) for val in tup]
    final_values = numpy.array([finalValues])
    
    scaler_X.fit_transform(X)
    scaler_y.fit_transform(y)
    inputs_scaled = scaler_X.transform(final_values)
    present_hygro_scaled = scaler_y.transform([hygro_01])
    present_hygro_scaled = present_hygro_scaled[0]
    inputs_scaled = inputs_scaled.reshape(1, 2, 3)
    
    predictions = loaded_model.predict(inputs_scaled)
    denormalized_predictions = scaler_y.inverse_transform(predictions)
    predictions = predictions[0]
    denormalized_predictions = denormalized_predictions[0]
    predictions_mean = float(predictions.mean())
    

    datastorePrediction, time = datastore.Entity(datastore_client.key("Predictions")), datetime.datetime.utcnow()
    formatted_time = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    datastorePrediction.update({
            'published_at': formatted_time,
            'present_normalized_hygro': [float(present_hygro_scaled[0]), float(present_hygro_scaled[1])],
            'normalized_hygro_predictions': [float(predictions[0]), float(predictions[1])],
            'hygro_predictions': [float(denormalized_predictions[0]), float(denormalized_predictions[1])],
            'irrigation': 'YES'
            })
    
    if predictions_mean < 0.5 or present_hygro_scaled[0] < 0.05 or present_hygro_scaled[1] < 0.05:
        requests.get("https://us-central1-irrigation1.cloudfunctions.net/start_watering")
    else:
        datastorePrediction.update({'irrigation': 'NO'})
    
    #datastore_client.put(datastorePrediction)

    return datastorePrediction