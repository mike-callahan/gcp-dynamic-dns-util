from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from requests import get
import argparse
import logging
import sys
import gcpdnslib
import pathlib
import daemon
import os
import grp
import signal
import daemon
import lockfile
import traceback, time

# setup logging
file_log_handler = logging.FileHandler(filename='dns.log')
stdout_log_handler = logging.StreamHandler(stream=sys.stdout)
log_handlers = [stdout_log_handler, file_log_handler]

logging.basicConfig(
    level=logging.INFO, 
    encoding='utf-8',
    format='[worker][%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=log_handlers
)

logger = logging.getLogger(__name__)

# Build api service
service = build('dns', 'v1')

# Read in config file
config = gcpdnslib.read_config('./config.json')
logger.info('Initial configuration file read successfully!')

def dynamicdns():

    # Get the IP that is currently in GCP DNS
    old_config = gcpdnslib.get_record(config, service)

    # Get the current external IP
    new_ip = gcpdnslib.get_public_ip()

    # Construct a new configuration
    new_config = gcpdnslib.construct_record(config, new_ip)

    logger.info(f'An external IP address of: {new_ip} was detected')
    logger.info(f"The current IP address in Google DNS is: {old_config['rrdatas'][0]}")

    # Compare them and update
    if gcpdnslib.compare_record(gcpdnslib.get_record(config, service), gcpdnslib.get_public_ip()) == False:
        logger.info('IP change detected. Updated Google DNS...')
        gcpdnslib.patch_record(new_config, service)
        logger.info('Google DNS Updated!')
    else:
        logger.info('Nothing to do!')

def every(delay, task):
  next_time = time.time() + delay
  while True:
    time.sleep(max(0, next_time - time.time()))
    try:
      task()
    except Exception:
      traceback.print_exc()
      # in production code you might want to have this instead of course:
      # logger.exception("Problem while executing repetitive task.")
    # skip tasks if we are behind schedule:
    next_time += (time.time() - next_time) // delay * delay + delay


every(600, dynamicdns)