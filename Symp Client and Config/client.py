import sys
import getpass
import requests
import yaml
import os
import symphony_client


def _load_config():
    root_path = os.path.dirname(os.path.abspath(__file__))
    try:
        with open('{}/cluster_config.yml'.format(root_path)) as YAML:
            try:
                config = yaml.safe_load(YAML)
                return config
            except yaml.YAMLError as yaml_error:
                print('Unable to load {}/cluster_config.txt.\nError:  {}\n'
                      'Exiting...'.format(root_path, yaml_error))
                sys.exit()
    except IOError as io_error:
        print('Unable to open "{}/cluster_config.yml".\n Error: {}\n'
              'Exiting...'.format(root_path, io_error))
        sys.exit()


def create_symphony_client():
    config_file = _load_config()
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
            client.login(
                domain=domain,
                username=username,
                password=getpass.getpass('Password:>\n '),
                project=config_file['project']
            )
            logged_in = True
        except requests.exceptions.HTTPError as login_error:
            print(login_error)
    return client
