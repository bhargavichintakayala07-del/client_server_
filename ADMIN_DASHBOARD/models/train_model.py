import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
import joblib

# Load dataset
data = pd.read_csv("dataset.csv")

# Input (website)
X = data["website"]

# Output (category)
y = data["category"]

# Convert text to numbers
vectorizer = CountVectorizer()
X_vector = vectorizer.fit_transform(X)

# Train model
model = DecisionTreeClassifier()
model.fit(X_vector, y)

# Save model
joblib.dump(model, "model.pkl")

# Save vectorizer
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ AI Model Trained Successfully!")
print("✅ model.pkl Created")
print("✅ vectorizer.pkl Created")