import json

import boto3

from vfs import *
from cache import LoadingCache


def simplify_dynamo_attr(attribute):
    if 'S' in attribute:
        return attribute['S']
    if 'N' in attribute:
        return attribute['N']
    return str(attribute)


def simplify_dynamo_item(attr_dict):
    return {k: simplify_dynamo_attr(v) for k, v in attr_dict.items()}


class DynamoDir(VDir):
    def __init__(self):
        self.children = None

    def get_children(self):
        if not self.children:
            self.children = [
                (region_name, DynamoRegionDir(region_name))
                for region_name
                in ["us-east-1", "us-west-2", "us-west-1", "eu-west-1",
                    "eu-central-1", "ap-southeast-1", "ap-northeast-1",
                    "sa-east-1"]]
        return self.children


class DynamoRegionDir(VDir):
    def __init__(self, region):
        self.region = region

        def load(_):
            db = boto3.client('dynamodb', region_name=self.region)
            result = []
            for page in db.get_paginator('list_tables').paginate():
                result += [
                    (table_name, DynamoTable(self.region, table_name))
                    for table_name in page['TableNames']]
            return result

        self.cache = LoadingCache(load, 60)

    def get_children(self):
        children = self.cache.get('children')
        return children


class DynamoTable(VDir):
    def __init__(self, region, table):
        self.region = region
        self.table = table
        self.db = boto3.client('dynamodb', region_name=self.region)

        def load(_):
            return self.load_rows()
        self.cache = LoadingCache(load, 60)

    def get_children(self):
        return self.cache.get('rows')

    def load_rows(self):
        key_col = self.load_key_col()
        result = []
        for page in self.db.get_paginator('scan').paginate(
                TableName=self.table,
                AttributesToGet=[key_col]):
            for item in page['Items']:
                key_attr = item[key_col]
                filename = simplify_dynamo_attr(key_attr)
                value = DynamoRow(self.region, self.table,
                                  key_col, key_attr)
                result.append((filename, value))
        return result

    def load_key_col(self):
        for key in (self.db.describe_table(TableName=self.table)
                    ['Table']['KeySchema']):
            if key['KeyType'] == 'HASH':
                return key['AttributeName']
        raise Exception('Table has no hash key!')


class DynamoRow(VFile):
    def __init__(self, region, table, key_col, key_attr):
        self.db = boto3.client('dynamodb', region_name=region)
        self.table = table
        self.key_obj = {key_col: key_attr}

        def load(_):
            return self.load_contents()
        self.cache = LoadingCache(load, 60)

    def read(self):
        return self.cache.get('contents')

    def write(self):
        pass

    def get_size(self):
        return len(self.read())

    def load_contents(self):
        item = self.db.get_item(TableName=self.table, Key=self.key_obj)['Item']
        return (json.dumps(simplify_dynamo_item(item),
                           sort_keys=True, indent=4) + '\n').encode()
