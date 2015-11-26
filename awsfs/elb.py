import boto3

from format import to_json
from vfs import *


def elb_root():

    return SDir([
        (region, CLDir(lambda _region=region: [
            (elb['LoadBalancerName'], SDir([
                ('info', SFile(to_json(elb).encode())),
                ('status', LFile(lambda _elb=elb: get_status_file(_region, _elb))),
                ('instances', SDir([
                    (elb_instance['InstanceId'], VLink('../../../../ec2/%s/instances/%s' %
                                                       (_region, elb_instance['InstanceId'])))
                    for elb_instance in elb['Instances']
                ])),
                ('security-groups', SDir([
                    (security_group_id, VLink('../../../../ec2/%s/security-groups/%s' %
                                              (_region, security_group_id)))
                    for security_group_id in elb['SecurityGroups']
                ]))
            ]))
            for elb in get_elbs(_region)
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
    return boto3.client('elb', region_name=region)


def get_elbs(region):
    return [
        elb
        for page in (get_client(region).
                     get_paginator('describe_load_balancers').
                     paginate())
        for elb in page['LoadBalancerDescriptions']
    ]


def get_status_file(region, elb):
    name = elb['LoadBalancerName']
    statuses = (get_client(region).
                describe_instance_health(LoadBalancerName=name)
                ['InstanceStates'])
    return to_json(statuses).encode()
