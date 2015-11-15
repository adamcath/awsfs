import boto3

from vfs import *
from cache import LoadingCache
from format import to_json


def get_client(region):
    return boto3.client('ec2', region_name=region)


class Ec2Dir(VDir):
    def __init__(self):
        VDir.__init__(self)
        self.children = [
                (region_name, Ec2RegionDir(region_name))
                for region_name
                in ["ap-northeast-1", "ap-southeast-1", "ap-southeast-2",
                    "eu-central-1", "eu-west-1", "sa-east-1", "us-east-1",
                    "us-west-1", "us-west-2"]]

    def get_children(self):
        return self.children


class Ec2RegionDir(VDir):
    def __init__(self, region):
        VDir.__init__(self)
        self.children = [
            ("instances", Ec2InstancesDir(region))]

    def get_children(self):
        return self.children


class Ec2InstancesDir(VDir):
    def __init__(self, region):
        VDir.__init__(self)
        self.region = region
        self.cache = LoadingCache(lambda _: self.miss(), 60)

    def get_children(self):
        return self.cache.get('instance-ids')

    def miss(self):
        result = []
        for page in (get_client(self.region).
                     get_paginator('describe_instances').
                     paginate()):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    result.append(
                        (instance_id,
                         Ec2InstanceDir(self.region, instance_id, instance)))
        return result


class Ec2InstanceDir(VDir):
    def __init__(self, region, instance_id, instance_obj):
        VDir.__init__(self)
        self.children = [
            ("info", StaticFile(to_json(instance_obj).encode())),
            ("status", Ec2InstanceStatusFile(region, instance_id))]

    def get_children(self):
        return self.children


class Ec2InstanceStatusFile(LazyReadOnlyFile):
    def __init__(self, region, instance_id):
        def load():
            statuses = (get_client(region).
                        describe_instance_status(InstanceIds=[instance_id])
                        ['InstanceStatuses'])
            if len(statuses) == 0:
                return 'null'
            return to_json(statuses[0]).encode()

        LazyReadOnlyFile.__init__(self, load)
