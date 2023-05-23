from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import numpy, pickle

scaler_X, scaler_y = MinMaxScaler(), MinMaxScaler()
loaded_model = load_model("neural_network.h5")

with open('X.pkl', 'rb') as f:
    X  = pickle.load(f)
        
with open('y.pkl', 'rb') as f:
    y = pickle.load(f)

X_scaled, y_scaled = scaler_X.fit_transform(X), scaler_y.fit_transform(y)

lux_01_SYS01 = numpy.array([1.0608,1.0519,1.05783,1.0519,1.0519,1.05783,1.0519,1.05783,1.05486,1.05783]).mean()
lux_01_SYS02 = numpy.array([3.88687,3.65379,3.93081,3.77914,3.80044,4.15811,4.22883,4.26464,4.46081,4.47337]).mean()

new_input = numpy.array([[21.9, 95.4, lux_01_SYS01, 22, 95, lux_01_SYS02]])
new_input_scaled = scaler_X.transform(new_input)
new_input_scaled = new_input_scaled.reshape(new_input_scaled.shape[0], 2, 3)
new_output_scaled = loaded_model.predict(new_input_scaled)
new_output = scaler_y.inverse_transform(new_output_scaled)

print("Normalized hygro_01 is", new_output_scaled)
print("hygro_01 is", new_output)