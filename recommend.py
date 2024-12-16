import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from scipy.sparse.linalg import svds

# Step 1: Load the Data
# Replace this path with your actual dataset path
data_path = '/mnt/data/Karnataka_Tourism_Dataset_With_Images.csv'

# Check if the file exists
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Dataset not found at {data_path}. Please check the file path and try again.")

# Read the dataset
data = pd.read_csv(data_path)

# Step 2: Data Preprocessing
# Ensure the dataset has 'user_id', 'placeID', 'rating' columns
if not {'user_id', 'placeID', 'rating'}.issubset(data.columns):
    raise ValueError("Dataset must contain 'user_id', 'placeID', and 'rating' columns.")

# Create a user-item interaction matrix
user_item_matrix = data.pivot(index='user_id', columns='placeID', values='rating').fillna(0)

# Convert the matrix to a NumPy array for computations
R = user_item_matrix.values

# Normalize ratings (centered around the mean)
user_means = np.mean(R, axis=1)
R_demeaned = R - user_means.reshape(-1, 1)

# Step 3: SVD - Singular Value Decomposition
# Decompose the matrix into three components: U, Sigma, Vt
U, sigma, Vt = svds(R_demeaned, k=50)  # k is the number of latent features
sigma = np.diag(sigma)

# Reconstruct the predicted ratings matrix
R_predicted = np.dot(np.dot(U, sigma), Vt) + user_means.reshape(-1, 1)
predicted_ratings = pd.DataFrame(R_predicted, columns=user_item_matrix.columns)

# Step 4: Recommendation Logic
def get_top_recommendations(user_id, predicted_ratings, original_data, n=5):
    """
    Recommend top N places for a given user based on predicted ratings.
    """
    # Ensure user_id exists in the dataset
    if user_id not in original_data['user_id'].unique():
        return "User not found. Try a different user_id."
    
    # Get user's predicted ratings
    user_idx = original_data[original_data['user_id'] == user_id].index[0]
    user_ratings = predicted_ratings.iloc[user_idx]
    
    # Get already rated places
    rated_places = original_data[original_data['user_id'] == user_id]['placeID'].tolist()

    # Exclude already rated places
    recommendations = user_ratings.drop(labels=rated_places).sort_values(ascending=False).head(n)
    return recommendations

# Example: Get top 5 recommendations for user_id=1
user_id = 1
top_places = get_top_recommendations(user_id, predicted_ratings, data, n=5)

# Print recommendations
print("Top 5 recommended places:")
for place_id, score in top_places.items():
    print(f"Place ID: {place_id}, Predicted Rating: {score:.2f}")

# Step 5: Evaluation
def calculate_rmse(original_matrix, predicted_matrix):
    """
    Calculate RMSE to evaluate the prediction accuracy.
    """
    mask = original_matrix != 0  # Only compare for non-zero ratings
    mse = mean_squared_error(original_matrix[mask], predicted_matrix[mask])
    return np.sqrt(mse)

rmse = calculate_rmse(R, R_predicted)
print(f"Root Mean Square Error (RMSE): {rmse:.2f}")

# Step 6: Handling Cold Start
def handle_cold_start(user_id=None, n=5):
    """
    Recommend top N places based on average ratings for new users.
    """
    top_rated = data.groupby('placeID')['rating'].mean().sort_values(ascending=False).head(n)
    return top_rated

# Example: Cold start recommendations
print("Cold start recommendations (top-rated places):")
cold_start_places = handle_cold_start(n=5)
print(cold_start_places)