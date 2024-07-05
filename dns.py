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



context = daemon.DaemonContext(
    working_directory='/etc/gcpdyndns/',
    umask=0o002,
    pidfile=lockfile.FileLock('/var/run/gcpdyndns.pid'),
    )

context.signal_map = {
    signal.SIGTERM: gcpdnslib.shutdown(),
    signal.SIGHUP: 'terminate',
    signal.SIGUSR1: gcpdnslib.reload_config(),
    }

mail_gid = grp.getgrnam('mail').gr_gid
context.gid = mail_gid

important_file = open('spam.data', 'w')
interesting_file = open('eggs.data', 'w')
context.files_preserve = [important_file, interesting_file]

initial_program_setup()

with context:
    do_main_program()

# parse shell arguments
parser = argparse.ArgumentParser(
    description='Dynamic DNS Utility for GCP')
parser.add_argument(
    'config', help='Path to configuration file.')
parser.add_argument(
    '--log', default=sys.stdout, type=argparse.FileType('w'),
    help='Where to write logs.')
args = parser.parse_args()

# setup logging
file_log_handler = logging.FileHandler(filename='dyndns.log')
stdout_log_handler = logging.StreamHandler(stream=sys.stdout)
log_handlers = [stdout_log_handler, file_log_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    encoding='utf-8',
    format='[worker][%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=log_handlers
)

logger = logging.getLogger(__name__)


# Build api service
service = build('dns', 'v1')

# Read in config file
config = gcpdnslib.read_config(args.config)

# Get the IP that is currently in GCP DNS
old_config = gcpdnslib.get_record(config, service)

# Get the current external IP
new_ip = gcpdnslib.get_public_ip()

# Construct a new configuration
new_config = gcpdnslib.construct_record(config, new_ip)

# Compare them and update
if gcpdnslib.compare_record(gcpdnslib.get_record(
        config, service), gcpdnslib.get_public_ip()) == False:
    gcpdnslib.patch_record(new_config, service)

print()
# patch_record()
print(gcpdnslib.get_public_ip())
print(gcpdnslib.get_record(config, service))
# print(patch_record())
print(new_config)
