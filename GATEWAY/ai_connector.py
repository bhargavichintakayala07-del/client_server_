import csv


def predict(domain):

    try:

        with open("dataset.csv", "r") as file:

            reader = csv.DictReader(file)

            for row in reader:

                if row["website"].lower() == domain.lower():

                    return {
                        "status": row["status"],
                        "category": row["category"]
                    }

    except Exception as e:

        print("Error:", e)

    return {
        "status": "Unknown",
        "category": "Unknown"
    }