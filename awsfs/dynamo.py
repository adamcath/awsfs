import boto3
from vfs import *
from format import to_json


def dynamo_root():

    return SDir([
        (region, CLDir(lambda _region=region: [
            (table, CLDir(lambda _table=table: [
                (key_name, LFile(lambda _key=key_name, _key_col=key_col, _key_attr=key_attr:
                                 get_item_file(_region, _table, _key_col, _key_attr)))
                for (key_name, key_col, key_attr) in get_keys(_region, _table)
            ]))
            for table in get_tables(_region)
        ]))
        for region in get_regions()
    ])


def get_regions():
    return [
        "us-east-1", "us-west-2", "us-west-1", "eu-west-1",
        "eu-central-1", "ap-southeast-1", "ap-northeast-1",
        "sa-east-1"
    ]


def get_client(region):
    return boto3.client('dynamodb', region_name=region)


def get_tables(region):
    return [
        table
        for page in get_client(region).get_paginator('list_tables').paginate()
        for table in page['TableNames']
    ]


def get_keys(region, table):
    key_col = get_key_col(region, table)
    result = []
    for page in (get_client(region).
                 get_paginator('scan').
                 paginate(TableName=table, AttributesToGet=[key_col])):
        for item in page['Items']:
            key_attr = item[key_col]
            result.append((simplify_dynamo_attr(key_attr), key_col, key_attr))
    return result


def get_key_col(region, table):
    for key in (get_client(region).describe_table(TableName=table)
                ['Table']['KeySchema']):
        if key['KeyType'] == 'HASH':
            return key['AttributeName']
    raise Exception('Table has no hash key!')


def get_item_file(region, table, key_col, key_attr):
    return (
        to_json(
            simplify_dynamo_item(
                get_client(region).
                get_item(TableName=table, Key={key_col: key_attr})
                ['Item'])
        ).encode())


def simplify_dynamo_attr(attribute):
    if 'S' in attribute:
        return attribute['S']
    if 'N' in attribute:
        return attribute['N']
    return str(attribute)


def simplify_dynamo_item(attr_dict):
    return {k: simplify_dynamo_attr(v) for k, v in attr_dict.items()}
