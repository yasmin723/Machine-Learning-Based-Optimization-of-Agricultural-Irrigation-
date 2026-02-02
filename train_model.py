import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
import joblib
import os

# Load your dataset - Ensure the file exists in the /model folder
data = pd.read_csv('modified_crop_recommendation_dataset.csv')

# Features based on Student Guide requirements
X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['soil_moisture'] 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 1. Random Forest (Target: 94% R2)
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
joblib.dump(rf, 'irrigation_model.pkl')

# 2. Neural Network (Target: 93% R2)
nn = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
nn.fit(X_train, y_train)
joblib.dump(nn, 'nn_model.pkl')

# 3. Gradient Boosting (Target: 89% R2)
gb = GradientBoostingRegressor(n_estimators=100, random_state=42)
gb.fit(X_train, y_train)
joblib.dump(gb, 'gb_model.pkl')

# 4. SVM (Target: 82% R2)
svm = SVR(kernel='rbf')
svm.fit(X_train, y_train)
joblib.dump(svm, 'svm_model.pkl')

print("All 4 models trained and saved successfully!")