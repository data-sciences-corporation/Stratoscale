import getpass
import os
import sys

import requests
import symphony_client
import yaml.loader


def load_config():
    """Checks for existence of config file. If an error occurs, program exits.
    If found, returns config file as YAML"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    try:
        with open("{}/config.yml".format(root_path)) as YAML:
            try:
                config = yaml.safe_load(YAML)
            except yaml.YAMLError as yaml_exception:
                print('Unable to load "{}/config.yml".\nError: {}\n'
                      'Exiting...'.format(root_path, yaml_exception))
                sys.exit()
    except IOError as io_error:
        print('Unable to open "{}/config.yml".\n Error: {}\n'
              'Exiting...'.format(root_path, io_error))
        sys.exit()
    return config


def create_symp_client():
    """Create a symphony client and log in to the cluster
    :return client: A Symphony Client Session"""
    config_file = load_config()
    session = requests.Session()
    session.trust_env = False
    if not config_file['verify_ssl']:
        session.verify = False
    elif config_file['cert_file'] is not None:
        session.cert = config_file['cert_file']
    client = symphony_client.Client(
        url='https://{}'.format(config_file['cluster_ip']),
        session=session
    )
    logged_in = False
    while not logged_in:
        domain = config_file['domain']
        username = config_file['username']
        domain_temp = raw_input('Domain [{}]:\n> '.format(domain))
        username_temp = raw_input('Username [{}]:\n> '.format(username))
        if domain_temp:
            domain = domain_temp
        if username_temp:
            username = username_temp
        try:
            client.login(domain=domain,
                         username=username,
                         password=getpass.getpass('Password:\n> '),
                         project=config_file['project'])
            logged_in = True
        except requests.exceptions.HTTPError as login_error:
            print '\n\n{}\nUnable to log in.\nPlease verify your credentials'.format(login_error)
    return client
