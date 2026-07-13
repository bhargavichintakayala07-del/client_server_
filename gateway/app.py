from flask import Flask, render_template, request
import tldextract

from ai_connector import predict
from logger import save_log

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/access", methods=["POST"])
def access():

    website = request.form["website"]

    extracted = tldextract.extract(website)
    domain = extracted.domain + "." + extracted.suffix

    decision = predict(domain)

    save_log(domain, decision)

    print("\n========== REQUEST RECEIVED ==========")
    print("Original URL :", website)
    print("Extracted Domain :", domain)
    print("Decision :", decision)
    print("======================================\n")

    if decision == "Allowed":
        return f"""
        <h2 style='color:green;'>✅ Website Allowed</h2>

        <p><b>Website:</b> {domain}</p>

        <p><b>Status:</b> {decision}</p>
        """

    elif decision == "Blocked":
        return f"""
        <h2 style='color:red;'>🚫 Access Denied</h2>

        <p><b>Website:</b> {domain}</p>

        <p><b>Status:</b> {decision}</p>
        """

    else:
        return f"""
        <h2 style='color:orange;'>⚠ Unknown Website</h2>

        <p><b>Website:</b> {domain}</p>

        <p>This domain is not present in the AI database.</p>
        """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)