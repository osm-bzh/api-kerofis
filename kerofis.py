from flask import Flask
app = Flask(__name__)

@app.route("/kerofis/")
def hello():
    return "API kerofis"

if __name__ == "__main__":
    app.run()

