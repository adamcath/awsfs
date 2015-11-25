import boto3

from format import to_json
from vfs import *


def ec2_root():
    return SDir([
        (region, SDir([
            ('instances', CLDir(lambda _region=region: [
                (instance['InstanceId'], SDir([
                    ('info', SFile(to_json(instance).encode())),
                    ('status', LFile(lambda _instance=instance:
                                     get_instance_status(_region, _instance['InstanceId']))),
                    ('security-groups', SDir(get_instance_security_group_dirents(instance)))
                ]))
                for instance in get_instances(_region)
            ])),
            ('security-groups', CLDir(lambda _region=region: ([
                (group['GroupId'], SDir([
                    ('info', SFile(to_json(group).encode()))
                ]))
                for group in get_security_groups(_region)
            ] + [
                ('by-name',
                 SDir([
                     (group['GroupName'], VLink('../' + group['GroupId']))
                     for group in get_security_groups(_region) if 'GroupName' in group
                 ]))
            ])))
        ]))
        for region in get_regions()
    ])


def get_regions():
    return [
        "ap-northeast-1", "ap-southeast-1", "ap-southeast-2",
        "eu-central-1", "eu-west-1", "sa-east-1", "us-east-1",
        "us-west-1", "us-west-2"
    ]


def get_client(region):
    return boto3.client('ec2', region_name=region)


def get_instances(region):
    return [
        instance
        for page in (get_client(region).
                     get_paginator('describe_instances').
                     paginate())
        for reservation in page['Reservations']
        for instance in reservation['Instances']
    ]


def get_instance_status(region, instance_id):
    statuses = (get_client(region).
                describe_instance_status(InstanceIds=[instance_id])
                ['InstanceStatuses'])
    return (to_json(statuses[0]).encode()
            if len(statuses) > 0
            else 'null'.encode())


def get_instance_security_group_dirents(instance):
    return [
        (group['GroupId'],
         VLink('../../../security-groups/' + group['GroupId']))
        for group in instance['SecurityGroups']
    ]


def get_security_groups(region):
    return get_client(region).describe_security_groups()['SecurityGroups']
