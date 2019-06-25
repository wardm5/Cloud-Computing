from flask import Flask
import boto3
from boto3.dynamodb.conditions import Key, Attr
import time
import unicodedata
import json
import os
import requests

s3 = boto3.resource('s3',
    region_name='us-east-1')
dynamodb = boto3.resource('dynamodb',
    region_name='us-east-1')

# dynamodb = boto3.resource('dynamodb',
#     region_name='us-east-1',
#     aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
#     aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
# s3 = boto3.resource("s3")
bucket_name = "mishaward2462890"
full_path = "test.txt"

# def main():
#     # create_DB()
#     # load()
#     # clear()
#     # create_DB()
#     test = {
#         # 'last_name' : "Howitt",
#         'first_name' : "Janway"
#     }
#     f_name = "Howitt"
#     l_name = ""
#     query(test)

def load():
    #target_url = "https://s3-us-west-2.amazonaws.com/drdoran-program4/data80entries2.txt"
    # target_url = "https://s3-us-west-2.amazonaws.com/drdoran-program4/data80entries.txt"
     target_url = "https://s3-us-west-2.amazonaws.com/css490/input.txt"
    # 1) load data
    # load aws
    response = requests.get(target_url)
    response.encoding = 'utf-8'
    data = response.text.strip()
    split = data.split("\n")
    # load DynamoDB
    for i in range(len(split)):
        split2 = split[i].split(' ')
        first_name = split2[0]
        last_name = split2[1]
        jsonObj = {}
        for j in range(2, len(split2)):
            dataPoint = split2[j].strip()
            if dataPoint:
                splitData = dataPoint.split("=")
                jsonObj[splitData[0]] = splitData[1]
        print(jsonObj)
        load_db(last_name, first_name, json.dumps(jsonObj))
    # load s3
    aws_s3(data)

def aws_s3(data):
    s3.create_bucket(Bucket=bucket_name,ACL='public-read')
    s3.Object(bucket_name, full_path).put(Body=data,ACL='public-read')

def load_db(last, first, data_blob):
    table = dynamodb.Table('Database')
    table.put_item(
        TableName='Database',
        Item={
            'last_name': first,
            'first_name': last,
            'data': data_blob
        }
    )

def create_DB():
    # Get the service resource.
    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName='Database',
        KeySchema=[
            {
                'AttributeName': 'last_name',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'first_name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'last_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'first_name',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName='Database')
    return table

def delete_DB():
    # dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    # table = dynamodb.Table('Database')
    # table.delete()

    client = boto3.client('dynamodb')
    client.delete_table(TableName='Database')
    waiter = client.get_waiter('table_not_exists')
    waiter.wait(TableName='Database')
    print("table deleted")


def clear():
    s3.Object(bucket_name, full_path).delete()  # clears s3 bucket
    delete_DB()
    create_DB()

def query(data):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('Database')
    first_name  = None
    last_name = None
    key = None
    if 'first_name' in data:
        first_name = data['first_name']
    if 'last_name' in data:
        last_name = data['last_name']
    response = None
    if first_name and last_name:
        # query "firstname lastname"
        response = table.get_item(
            Key={
                'first_name': first_name,
                'last_name': last_name
            }
        )
    elif first_name:
        fe = Key('first_name').eq(first_name)

        response = table.scan(
            FilterExpression=fe
        )


    elif last_name:
        print("some other rando-pando")
        response = table.query(
            KeyConditionExpression=Key('last_name').eq(last_name)
        )
    return response

# main()
