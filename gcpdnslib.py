from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from requests import get
import os
import shutil


def read_config(filepath) -> map:
    with open(filepath, "r") as json_file:
        data = json.load(json_file)
    return data


def get_public_ip() -> str:
    ip_address = get('http://ip-api.com/json').content.decode('utf8')
    ip_address = json.loads(ip_address)
    return ip_address['query']


def get_record(config, service) -> str:
    request = service.resourceRecordSets().get(
        project=config['gcpProjectId'],
        managedZone=config['managedZone'],
        name=config['record']['name'],
        type=config['record']['type'])
    response = request.execute()
    return response


def patch_record(config, service) -> str:
    request = service.resourceRecordSets().patch(
        project=config['gcpProjectId'],
        managedZone=config['managedZone'],
        name=config['record']['name'],
        type=config['record']['type'], body=config['record'])
    response = request.execute()
    return response


def compare_record(get_record, get_public_ip) -> bool:
    current = get_record['rrdatas'][0]
    updated = get_public_ip
    if current != updated:
        return False


def construct_record(config, public_ip) -> dict:
    config['record']['rrdatas'] = [public_ip]
    return config

def setup_daemon():
    return NotImplementedError()

def listen_for_changes():
    return NotImplementedError()

def reload_config():
    return NotImplementedError()

def shutdown():
    return NotImplementedError()
