import joblib

model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

website = input("Enter Website: ")

website_vector = vectorizer.transform([website])

prediction = model.predict(website_vector)

print("Prediction:", prediction[0])