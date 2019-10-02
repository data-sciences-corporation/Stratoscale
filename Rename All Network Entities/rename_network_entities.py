#!/usr/bin/env python
# coding: utf-8
"""Script to rename network entities to a defined convention"""
import sys
import os
import yaml
import requests
from resource.symp_client import create_symp_client


def clear():
    """Clears the terminal"""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def load_config():
    """Checks for existance of config file. If an error occurs, program exits.
    If found, returns config file as YAML"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    try:
        with open("{}/resource/config.yml".format(root_path)) as config_file:
            try:
                config = yaml.safe_load(config_file)
            except yaml.YAMLError as yaml_exception:
                print('Unable to load "{}/config.yml".\nError: {}\n'
                      'Exiting...'.format(root_path, yaml_exception))
                sys.exit()
    except IOError as io_error:
        print('Unable to open "{}/config.yml".\n Error: {}\n'
              'Exiting...'.format(root_path, io_error))
        sys.exit()
    return config


def set_format():
    """
    Prompts the user for a format they desire
    :return user_format: String with placeholders to specify name format
    """
    user_format = '{}_{}_{}'
    valid = False
    while not valid:
        new_format = raw_input("\n\n"
                               "Please note: Entity type names are set in the config.yml file.\n"
                               "Please select a desired format by entering "
                               "the corresponding number.\n"
                               "\tformat | example\n"
                               "\t1. entity.type_domain_project | vpc_engineering_dev [Default]\n"
                               "\t2. entity.type_project_domain | vpc_dev_engineering\n"
                               "\t3. domain_entity.type_project | engineering_vpc_dev\n"
                               "\t4. domain_project_entity.type | engineering_dev_vpc\n"
                               "\t5. project_entity.type_domain | dev_vpc_engineering\n"
                               "\t6. project_domain_entity.type | dev_engineering_vpc\n"
                               "> ")
        try:
            new_format = int(new_format)
            if 0 < user_format < 7:
                valid = True
        except ValueError as value_error:
            print('Invalid Input.\nError: {}'.format(value_error))
            valid = False

    if new_format:
        if new_format == 1:
            user_format = '{0}_{1}_{2}'
        elif new_format == 2:
            user_format = '{0}_{2}_{1}'
        elif new_format == 3:
            user_format = '{1}_{0}_{2}'
        elif new_format == 4:
            user_format = '{1}_{2}_{0}'
        elif new_format == 5:
            user_format = '{2}_{0}_{1}'
        elif new_format == 6:
            user_format = '{2}_{1}_{0}'
    else:
        user_format = '{0}_{1}_{2}'
    return  user_format


def rename_net(data, entity_type, client):
    """
    Uses network entity data to create a new name based on convention
    :param data: data retrieved when executing <entity>.list()
    :param entity_type: Type of entity, should match name specified in config
    :return: string of any and all exceptions that occurred during the rename process
    """
    to_string = "============================================"
    renamed = list()
    entity_exceptions_list = list()
    for entity in data:
        entity_id = entity['id']
        entity_old_name = entity['name']
        try:
            project_data = client.projects.get(entity['project_id'])
            entity_new_name = FORMAT.format(entity_type,
                                            project_data['domain_name'],
                                            project_data['name'])
            counter = 0
            addable = False
            while not addable:
                counter += 1
                if entity_new_name in renamed:
                    if counter <= 1:
                        entity_new_name = "{}_{}".format(entity_new_name, counter)
                    else:
                        index = entity_new_name.rfind('_')
                        entity_new_name = entity_new_name[1:index - 1]
                        entity_new_name = "{}_{}".format(entity_new_name, counter)
                else:
                    addable = True
            print("{} --> {}".format(entity_old_name, entity_new_name))
            if entity_type == VPC:
                client.vpcs.update(name=str(entity_new_name),
                                   vpc_id=entity_id)
                renamed.append(entity_new_name)
            elif entity_type == ROUTE_TABLE:
                client.vpcs.route_tables.update(name=str(entity_new_name),
                                                route_table_id=entity_id)
            elif entity_type == GATEWAY:
                client.vpcs.internet_gateways.update(name=str(entity_new_name),
                                                     internet_gateway_id=entity_id)
            elif entity_type == DHCP:
                client.vpcs.dhcp_options.update(name=str(entity_new_name),
                                                dhcp_options_id=entity_id)
            else:
                entity_exceptions_list.append("ENTITY TYPE NOT FOUND")
        except requests.exceptions.HTTPError as httpexception:
            entity_exceptions_list.append("\nError occurred on {}.\n"
                                          "Exception: {}".format(entity_old_name, httpexception))
    print("\nRename complete\n")
    if entity_exceptions_list:
        to_string = to_string + "\nThe following Errors occurred when renaming " \
                                "{}:\n".format(entity_type)
        for exception in entity_exceptions_list:
            to_string = to_string + " " + exception
    return to_string


def rename_all(client):
    """
    Calls the relevant functions to rename each entity type.
    Prevents the need to rewrite code for each entity type by calling network_entity_convention
    :return:
    """
    print("Renaming all network elements...")
    print("\nCollecting VPC data...")
    all_vpc_data = client.vpcs.list()
    print("VPC data collected. Processing VPCs...")
    if all_vpc_data:
        vpc_exceptions = rename_net(all_vpc_data, VPC, client)
    print("VPC processing complete.")

    print("\nCollecting Route Tables data...")
    all_routetable_data = client.vpcs.route_tables.list()
    print("Route Table data collected. Processing Route Tables...")
    if all_routetable_data:
        router_exceptions = rename_net(all_routetable_data, ROUTE_TABLE, client)
    print("Route Table processing complete.")

    print("\nCollecting Internet Gateways data...")
    all_gateways_data = client.vpcs.internet_gateways.list()
    print("Gateway data collected. Processing Internet Gateways")
    if all_gateways_data:
        gateway_exceptions = rename_net(all_gateways_data, GATEWAY, client)
    print("Internet Gateway processing complete")

    print("\nCollecting DHCP Options Sets data...")
    all_dhcp_data = client.vpcs.dhcp_options.list()
    print("DHCP Options Sets data collected. Processing...")
    if all_dhcp_data:
        dhcp_exceptions = rename_net(all_dhcp_data, DHCP, client)

    print("{}\n{}\n{}\n{}".format(vpc_exceptions,
                                  router_exceptions,
                                  gateway_exceptions,
                                  dhcp_exceptions))


def select_task(client):
    """Asks the user which action they would like to perform
    :param client: A symphony client session"""
    valid = False
    while not valid:
        chosen = raw_input('Select a task by entering the corresponding number.\n'
                           'Rename to convention:\n'
                           '\t1. All Network Entities.\n'
                           '\t2. VPCs.\n'
                           '\t3. Route Tables.\n'
                           '\t4. Internet Gateways.\n'
                           '\t5. DHCP Options Sets\n'
                           '> ')
        try:
            chosen = int(chosen)
            if 0 < chosen < 6:
                valid = True
            else:
                print('Invalid Input')
        except ValueError as value_error:
            print('Invalid Input.\nError: {}'.format(value_error))
            valid = False
    if chosen == 1:
        rename_all(client)
    elif chosen == 2:
        vpc_data = client.vpcs.list()
        rename_net(vpc_data, VPC, client)
    elif chosen == 3:
        rt_data = client.vpcs.route_tables.list()
        rename_net(rt_data, ROUTE_TABLE, client)
    elif chosen == 4:
        gw_data = client.vpcs.internet_gateways.list()
        rename_net(gw_data, GATEWAY, client)
    elif chosen == 5:
        dhcp_data == client.vpcs.dhcp_options.list()
        rename_net(dhcp_data, DHCP, client)
    else:
        print('Invalid Input')
    print('Rename Complete!\n'
          'Please note: If you are seeing any "Error: Not Found" it is most likely'
          ' due to entities that belong to the admin account.\n'
          'These entities by default do not belong to a Project and will therefor cause the error.')


def main():
    clear()
    client = create_symp_client()
    select_task(client)


CONFIG = load_config()
ENTITY_NAMES = CONFIG['entity_names']
VPC = ENTITY_NAMES['vpc']
ROUTE_TABLE = ENTITY_NAMES['route_tables']
GATEWAY = ENTITY_NAMES['internet_gateways']
DHCP = ENTITY_NAMES['dhcp_options_sets']

FORMAT = set_format()

if __name__ == '__main__':
    sys.exit(main())
