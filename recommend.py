# Import required libraries
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Load the dataset
file_path = "Tourist_Places_India.csv"  # Path to your dataset
data = pd.read_csv(file_path)

# Display the dataset structure
print("Dataset Head:\n", data.head())

# -------- Step 1: Content-Based Filtering --------
# Combine features for TF-IDF vectorization
data['CombinedFeatures'] = data['Type'] + " " + data['Activity'] + " " + data['Festival']

# Apply TF-IDF vectorization
tfidf = TfidfVectorizer(stop_words="english")
content_matrix = tfidf.fit_transform(data['CombinedFeatures'])

# Compute cosine similarity for places
content_similarity = cosine_similarity(content_matrix)
print("\nContent Similarity Matrix Shape:", content_similarity.shape)

# -------- Step 2: Collaborative Filtering --------
# Create a mock user-rating matrix (simulated for demonstration)
# Place IDs are rows, user IDs are columns
user_ratings = pd.DataFrame({
    1: [4.0, 3.5, np.nan, 4.5, 5.0],
    2: [np.nan, 4.0, 4.5, 3.0, np.nan],
    3: [5.0, 4.0, 3.5, np.nan, 2.0],
    4: [3.5, 2.0, np.nan, 4.5, 3.5],
    5: [np.nan, 3.5, 4.0, 5.0, 4.5]
}, index=[1, 2, 3, 4, 5])  # Place IDs

# Fill NaN values with 0 for similarity calculation
user_ratings_filled = user_ratings.fillna(0)

# Compute user-user similarity
collaborative_similarity = cosine_similarity(user_ratings_filled.T)
print("\nCollaborative Similarity Matrix Shape:", collaborative_similarity.shape)

# -------- Step 3: Hybrid Recommendation --------
# Combine collaborative and content-based similarities
# Normalize both similarity matrices
content_similarity_norm = (content_similarity - np.min(content_similarity)) / (np.max(content_similarity) - np.min(content_similarity))
collaborative_similarity_norm = (collaborative_similarity - np.min(collaborative_similarity)) / (np.max(collaborative_similarity) - np.min(collaborative_similarity))

# Generate hybrid similarity score (weighted average)
alpha = 0.5  # Weight for content-based filtering
beta = 0.5   # Weight for collaborative filtering
hybrid_similarity = alpha * content_similarity_norm + beta * collaborative_similarity_norm[:content_similarity.shape[0], :content_similarity.shape[0]]

# -------- Step 4: Training and Testing --------
# Prepare training data
# Features: Content similarity score and collaborative similarity score
data['ContentScore'] = np.mean(content_similarity_norm, axis=1)
data['CollaborativeScore'] = np.mean(collaborative_similarity_norm[:content_similarity.shape[0], :content_similarity.shape[0]], axis=1)
data['Target'] = data['Price per night']  # Use price as the target for demonstration

X = data[['ContentScore', 'CollaborativeScore']]
y = data['Target']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print("\nMean Squared Error:", mse)

def recommend_places(place_index, similarity_matrix, data, top_n=5):
    similarity_scores = list(enumerate(similarity_matrix[place_index]))
    sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    recommended_indices = [i[0] for i in sorted_scores[1:top_n+1]]  # Exclude itself
    return data.iloc[recommended_indices]
