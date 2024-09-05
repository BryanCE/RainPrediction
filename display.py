import tensorflow as tf
import numpy as np
import json
import matplotlib.pyplot as plt

with open('2014-2023_precip_by_grid.json', 'r') as f:
    data = json.load(f)


processed_data = []
for grid_id, grid_data in data.items():
    for year_data in grid_data:
        year = year_data['Year']
        for month_data in year_data['Month_Data']:
            month = month_data['Month']
            rainfall = month_data['Total_Rainfall_mm']
            processed_data.append((grid_id, year, month, rainfall))

# tensors ------------------------------------------------------------------------------------------------
grid_ids, years, months, rainfalls = zip(*processed_data)

grid_ids = tf.convert_to_tensor(grid_ids, dtype=tf.int32)
years = tf.convert_to_tensor(years, dtype=tf.int32)
months = tf.convert_to_tensor(months, dtype=tf.int32)
rainfalls = tf.convert_to_tensor(rainfalls, dtype=tf.float32)

#build and train model ------------------------------------------------------------------------------------------------
inputs = tf.keras.layers.Input(shape=(3,), name='input_layer')
x = tf.keras.layers.Dense(64, activation='relu')(inputs)
outputs = tf.keras.layers.Dense(1, name='output_layer')(x)

model = tf.keras.Model(inputs=inputs, outputs=outputs)
model.compile(optimizer='adam', loss='mse')

model.fit({'input_layer': tf.stack([grid_ids, years, months], axis=1)}, rainfalls, epochs=10)

#Predict on new data ------------------------------------------------------------------------------------------------
new_grid_ids = [6196, 6197, 6198]  # Example grid IDs
new_years = [2020, 2020, 2021]
new_months = [6, 7, 8]

new_inputs = tf.stack([tf.convert_to_tensor(new_grid_ids, dtype=tf.int32),
                       tf.convert_to_tensor(new_years, dtype=tf.int32),
                       tf.convert_to_tensor(new_months, dtype=tf.int32)], axis=1)

predicted_rainfalls = model.predict(new_inputs)
# print(predicted_rainfalls)

#Visualize predictions ------------------------------------------------------------------------------------------------

# Get predictions for a specific grid ID
grid_id = 6196
grid_predictions = predicted_rainfalls[new_grid_ids == grid_id]

# Create a line plot
months = [f"{year}-{month:02d}" for year, month in zip(new_years, new_months)]
plt.plot(months, grid_predictions)
plt.xlabel('Month')
plt.ylabel('Predicted Rainfall (mm)')
plt.title(f'Predicted Rainfall for Grid ID {grid_id}')
plt.show()
d = input("Press Enter to continue...")