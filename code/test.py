from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Route to send initial data to the client
@app.route('/')
def index():
    initial_data = {'a': 0, 'b': 1, 'c': 2}  # You can modify this data as needed
    return render_template('index.html', initial_data=initial_data)

# Route to dynamically update data on the client side
@app.route('/update_data')
def update_data():
    updated_data = {'Players': {"Player1":"Erik Van Doof","Player2":"Felix Schweigmann"}, 'c': 5}  # You can modify this data as needed
    return jsonify(updated_data)

if __name__ == '__main__':
    app.run(debug=True)
