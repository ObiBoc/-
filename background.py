from flask import Flask

app = Flask(__name__)

@app.route("/")
@app.route("/ping")
def ping():
    return "I'm alive", 200

def start_server():
    app.run(host="0.0.0.0", port=8000)
