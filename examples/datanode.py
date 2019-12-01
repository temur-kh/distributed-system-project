from flask import Flask, request, jsonify
import json

app = Flask(__name__)

PING_RESPONSE = '{"id": 1}'

@app.route("/", methods=['GET', 'POST'])
def process():
    json_d = request.get_json(force=True)
    
    return jsonify(PING_RESPONSE)

if __name__ == "__main__":

    app.run(port=2000)

