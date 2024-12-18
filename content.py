# Importing required libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Step 1: Load the dataset
file_path = "Tourist_Places_India.csv" 
data = pd.read_csv(file_path)

# Step 2: Data exploration
print("Dataset Head:")
print(data.head())

print("\nDataset Information:")
print(data.info())

# Step 3: Data preprocessing
# Select features for the model
features = ['Rating', 'No of People Visited', 'Type', 'Activities']
target = 'Price Per Night (₹)'

# One-hot encoding for categorical variables (Type and Activities)
categorical_features = ['Type', 'Activities']
encoder = OneHotEncoder()
encoded_features = encoder.fit_transform(data[categorical_features]).toarray()

# Combine encoded features with numerical features
numerical_features = data[['Rating', 'No of People Visited']].values
X = np.hstack([numerical_features, encoded_features])
y = data[target].values

# Step 4: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 5: Scaling features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Step 6: Model training
model = LinearRegression()
model.fit(X_train, y_train)

# Step 7: Model evaluation
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Evaluation:")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"R-squared (R2): {r2:.2f}")

# Step 8: Visualization
plt.scatter(y_test, y_pred, alpha=0.5)
plt.xlabel("Actual Prices")
plt.ylabel("Predicted Prices")
plt.title("Actual vs Predicted Prices")
plt.show()

# Step 9: Output analysis
coefficients = model.coef_
feature_names = ['Rating', 'No of People Visited'] + list(encoder.get_feature_names_out(categorical_features))
coef_df = pd.DataFrame({'Feature': feature_names, 'Coefficient': coefficients})

print("\nFeature Importance:")
print(coef_df)

# Step 10: Prediction example
sample_data = [[3.5, 12000, "Heritage", "Sightseeing"]]  # Example input
sample_df = pd.DataFrame(sample_data, columns=['Rating', 'No of People Visited', 'Type', 'Activities'])

# Encode and scale the sample
sample_encoded = encoder.transform(sample_df[['Type', 'Activities']]).toarray()
sample_numerical = sample_df[['Rating', 'No of People Visited']].values
sample_final = np.hstack([sample_numerical, sample_encoded])
sample_scaled = scaler.transform(sample_final)

# Predict the price
sample_prediction = model.predict(sample_scaled)
print(f"\nPredicted Price for the given sample data: ₹{sample_prediction[0]:.2f}")