import json
import sqlite3
from json import JSONDecodeError
from time import sleep
from urllib.parse import unquote_plus

from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/payment-credentials', methods=['POST'])
def payment_credentials():
    data = request.json

    try:
        data_object = json.loads(data)
    except JSONDecodeError as err:
        return 'Invalid data. ' + str(err), 400

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO paymentCredentials 
            (card, token) VALUES
            (?, ?);
            """,
            (data_object['card'], data_object['token'])
        )
    return 'Entry created', 201


@app.route('/pay', methods=['POST'])
def pay():
    sleep(3)
    raw_data = request.get_data(as_text=True)
    request_data = unquote_plus(raw_data)
    args = request_data.split('&')
    for a in args:
        k, v = a.split('=')
        if k == 'card':
            if v[-1] != '0' and int(v) % 2 == 0:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        SELECT token FROM paymentCredentials 
                        WHERE card = (?);
                        """,
                        (int(v),)
                    )
                    token = cursor.fetchone()[0]
                    cursor.execute(
                        """
                        DELETE FROM paymentCredentials
                        WHERE card = (?);
                        """,
                        (int(v),)
                    )
                resp = Response(json.dumps({'message': 'success', 'token': token}), 200)
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp
            else:
                resp = Response(json.dumps({'message': 'error', 'token': None}), 400)
                resp.headers['Access-Control-Allow-Origin'] = '*'
                return resp
    else:
        resp = Response(json.dumps({'message': 'error', 'token': None}), 400)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp


if __name__ == '__main__':
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS paymentCredentials 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            card INTEGER NOT NULL, 
            token VARCHAR(255) NOT NULL);
            """
        )
    app.run(host='0.0.0.0')
