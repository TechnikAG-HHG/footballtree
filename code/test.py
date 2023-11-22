from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/senddata', methods=['POST'])
def receive_data():
    output = request.json  # Assuming the data is sent in JSON format
    # Process the received data as needed
    print("Received data:", output)

    # Send a response back to the client
    response_data = {"message": "Data received successfully"}
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
