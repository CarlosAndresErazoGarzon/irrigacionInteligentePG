from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy, pandas, pickle

datasets = ['SYS01_1', 'SYS02_1']

for dataset in datasets:
    data = pandas.read_csv(dataset + '.csv')

    data['temp_01'] = data['temp_01'].apply(lambda x: numpy.mean(numpy.array(eval(x))))
    data['temp_02'] = data['temp_02'].apply(lambda x: numpy.mean(numpy.array(eval(x))))
    data['hum_01'] = data['hum_01'].apply(lambda x: numpy.mean(numpy.array(eval(x))))
    data['hum_02'] = data['hum_02'].apply(lambda x: numpy.mean(numpy.array(eval(x))))
    data['lux_01'] = data['lux_01'].apply(lambda x: numpy.mean(numpy.array(eval(x))))
    data['hygro_01'] = data['hygro_01'].apply(lambda x: numpy.mean(numpy.array(eval(x))))
        
    data.loc[data['temp_01'] <= 0, 'temp_01'] = data.loc[data['temp_01'] <= 0, 'temp_02']
    data.loc[data['hum_01'] <= 0, 'hum_01'] = data.loc[data['hum_01'] <= 0, 'hum_02']

    cols = ['temp_01', 'hum_01', 'lux_01', 'hygro_01']
        
    for col in cols:
        Q1, Q3 = numpy.percentile(data[col], [25, 75])
        IQR = Q3 - Q1 + 0.0000000001
        lower_bound, upper_bound = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            
        if (col == 'temp_01') or (col == 'hum_01'):
            for i in range(0, data[col].size) :
                cell_data = data.iloc[i, data.columns.get_loc(col)]
                
                if (cell_data < lower_bound) or (cell_data > upper_bound):
                    data.at[i, col] = data.iloc[i, data.columns.get_loc(col[:-1] + "2")]

        data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]

    data.to_csv(dataset + '_clean_data.csv', index=False)

SYS01_1 = pandas.read_csv('SYS01_1_clean_data.csv')

data = pandas.concat([SYS01_1, data])
data = data.sort_values(by='published_at')
data = data.reset_index(drop=True)

data['index'] = data.index
data.to_csv('merged_cleaned_data.csv', index=False)

data, groups = data.drop(columns=['device', 'published_at', 'temp_02', 'hum_02']), []

for i in range(0, len(data)-1, 2):
    groups.append(data.iloc[i:i+2])

data = pandas.concat(groups, ignore_index=True)
data = data[['temp_01', 'hum_01', 'lux_01', 'hygro_01', 'index']]

input_cols, output_cols, X, y = ['temp_01', 'hum_01', 'lux_01'], ['hygro_01'], [], []

for i in range(2, len(data)):
    if data.iloc[i]['index'] - data.iloc[i-2]['index'] == 2:
        X.append(data.iloc[i-2:i][input_cols].values)
        y.append(data.iloc[i-2:i][output_cols].values)

X, y = numpy.array(X), numpy.array(y)

x_samples, x_features1, x_features2 = X.shape
X = X.reshape(x_samples, x_features1 * x_features2)

y_samples, y_features1, y_features2 = y.shape
y = y.reshape(y_samples, y_features1 * y_features2)

scaler_X, scaler_y = MinMaxScaler(), MinMaxScaler()
X_scaled, y_scaled = scaler_X.fit_transform(X), scaler_y.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred_scaled = model.predict(X_test)
y_pred = scaler_y.inverse_transform(y_pred_scaled)
y_test_inv = scaler_y.inverse_transform(y_test)

with open('linear_regression.pkl', 'wb') as f:
    pickle.dump(model, f)
    
with open('X.pkl', 'wb') as f:
    pickle.dump(X, f)
    
with open('y.pkl', 'wb') as f:
    pickle.dump(y, f)