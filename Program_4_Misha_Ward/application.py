from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import awsCalls
from flask import Flask
from flask import Flask
import boto3
from boto3.dynamodb.conditions import Key, Attr
import time
import unicodedata
import json
import os
import requests

# A very basic API created using Flask that has two possible routes for requests.

application = Flask(__name__)
CORS(application)

# The service basepath has a short response just to ensure that healthchecks
# sent to the service root will receive a healthy response.
@application.route("/")
def healthCheckResponse():
    return jsonify({"message" : "Nothing here, used for health check. Try /getData instead."})

# The main API resource that the next version of the Mythical Mysfits website
# will utilize. It returns the data for all of the Mysfits to be displayed on
# the website.  Because we do not yet have any persistent storage available for
# our application, the mysfits are simply stored in a static JSON file. Which is
# read from the the filesystem, and directly used as the service response.
@application.route("/getData", methods=['GET'])
def getData():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    # get data from Dynamo DB
    response_data = awsCalls.query({
        'first_name': first_name,
        'last_name': last_name,
    })
    # response = Response(response_data)
    # set the Content-Type header so that the browser is aware that the response
    # is formatted as JSON and our frontend JavaScript code is able to
    # appropriately parse the response.
    # response.headers["Content-Type"] = "application/json"

    # print("================================================ end")
    return jsonify(response_data)

@application.route("/clearData", methods=['DELETE'])
def clearData():

    # clear data
    response = Response(awsCalls.clear())

    # set the Content-Type header so that the browser is aware that the response
    # is formatted as JSON and our frontend JavaScript code is able to
    # appropriately parse the response.
    response.headers["Content-Type"]= "application/json"

    return response

@application.route("/loadData", methods=['POST'])
def loadData():

    # read the mysfits JSON from the listed file.
    response = Response(awsCalls.load())

    # set the Content-Type header so that the browser is aware that the response
    # is formatted as JSON and our frontend JavaScript code is able to
    # appropriately parse the response.
    response.headers["Content-Type"]= "application/json"
    return response

# Run the service on the local server it has been deployed to,
# listening on port 8080.
if __name__ == "__main__":
    application.debug = True
    application.run(port=5000)
