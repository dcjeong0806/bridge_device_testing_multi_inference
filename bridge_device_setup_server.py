from flask import Flask, json, request, jsonify, make_response, Response
import datetime
import time
import threading
import os
import syslog

app = Flask(__name__)

def Log(log):
    print(log)

@app.route("/ServerInfo",methods=['GET'])
def ServerInfo():
    print("192.168.0.201 Server...")
    return jsonify({"ReplyStatusCode":200}),200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',port=9999)
