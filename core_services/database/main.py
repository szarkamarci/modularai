import os

import argparse

import yaml

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ger_start_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup_path', default = '')
    
    return parser.parse_args()

def main():
    setup_path = ger_start_args()

    if setup_path == '':
        logger.error("ERROR: Empty 'setup_param' argument")
        exit(1)

    try:
        with open(setup_path, 'r') as f:
            config_obj = yaml.load(f, Loader=yaml.SafeLoader)
    except Exception as e:
        logger.error(f"ERROR: unamble to tead {setup_path} as .yaml")
        exit(1)

    try:
        create_table(config_obj)
    except Exception as e:
        logger.error(f"ERROR: create_table() is FAILED by {config_obj}")
        exit(1)