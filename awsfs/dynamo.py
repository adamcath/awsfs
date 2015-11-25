import boto3
from vfs import *
from format import to_json


regions = [
    "us-east-1", "us-west-2", "us-west-1", "eu-west-1",
    "eu-central-1", "ap-southeast-1", "ap-northeast-1",
    "sa-east-1"
]


def get_client(region):
    return boto3.client('dynamodb', region_name=region)


def simplify_dynamo_attr(attribute):
    if 'S' in attribute:
        return attribute['S']
    if 'N' in attribute:
        return attribute['N']
    return str(attribute)


def simplify_dynamo_item(attr_dict):
    return {k: simplify_dynamo_attr(v) for k, v in attr_dict.items()}


def dynamo_root():

    def load():
        return [(region_name, dynamo_region(region_name))
                for region_name in regions]

    return CLDir(load, -1)


def dynamo_region(region):

    def load():
        result = []
        for page in get_client(region).get_paginator('list_tables').paginate():
            result += [
                (table_name, dynamo_table(region, table_name))
                for table_name in page['TableNames']]
        return result

    return CLDir(load, 60)


def dynamo_table(region, table):

    def load_key_col():
        for key in (get_client(region).describe_table(TableName=table)
                    ['Table']['KeySchema']):
            if key['KeyType'] == 'HASH':
                return key['AttributeName']
        raise Exception('Table has no hash key!')

    def load_rows():
        key_col = load_key_col()
        result = []
        for page in get_client(region).get_paginator('scan').paginate(
                TableName=table,
                AttributesToGet=[key_col]):
            for item in page['Items']:
                key_attr = item[key_col]
                filename = simplify_dynamo_attr(key_attr)
                value = dynamo_item(region, table,
                                    key_col, key_attr)
                result.append((filename, value))
        return result

    return CLDir(load_rows, 60)


def dynamo_item(region, table, key_col, key_attr):

    def load():
        return (
            to_json(
                simplify_dynamo_item(
                    get_client(region).
                    get_item(TableName=table, Key={key_col: key_attr})
                    ['Item'])
            ).encode())

    return LFile(load)
