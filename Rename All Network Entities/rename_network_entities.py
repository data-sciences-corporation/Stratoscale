import os
import sys

import requests
import yaml

import resource.validate as validate
from resource.symp_client import create_symp_client


def rename_net(data, entity_type, client):
    to_string = "============================================"
    renamed = list()
    entity_exceptions_list = list()
    for entity in data:
        entity_id = entity['id']
        entity_old_name = entity['name']
        try:
            project_data = client.projects.get(entity['project_id'])
            style = ENTITY_NAMES.style
            entity_new_name = style.format(entity_type,
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
            if entity_type == ENTITY_NAMES.vpc:
                client.vpcs.update(name=str(entity_new_name),
                                   vpc_id=entity_id)
                renamed.append(entity_new_name)
            elif entity_type == ENTITY_NAMES.route_table:
                client.vpcs.route_tables.update(name=str(entity_new_name),
                                                route_table_id=entity_id)
            elif entity_type == ENTITY_NAMES.gateway:
                client.vpcs.internet_gateways.update(name=str(entity_new_name),
                                                     internet_gateway_id=entity_id)
            elif entity_type == ENTITY_NAMES.dhcp:
                client.vpcs.dhcp_options.update(name=str(entity_new_name),
                                                dhcp_options_id=entity_id)
            else:
                entity_exceptions_list.append("ENTITY TYPE NOT FOUND")
        except requests.exceptions.HTTPError as http_exception:
            entity_exceptions_list.append("\nError occurred on {}.\n"
                                          "Exception: {}".format(entity_old_name, http_exception))
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
    vpc_exceptions = ''
    router_exceptions = ''
    gateway_exceptions = ''
    dhcp_exceptions = ''
    print("Renaming all network elements...")
    print("\nCollecting VPC data...")
    all_vpc_data = client.vpcs.list()
    print("VPC data collected. Processing VPCs...")
    if all_vpc_data:
        vpc_exceptions = rename_net(all_vpc_data, ENTITY_NAMES.vpc, client)
    print("VPC processing complete.")

    print("\nCollecting Route Tables data...")
    all_routetable_data = client.vpcs.route_tables.list()
    print("Route Table data collected. Processing Route Tables...")
    if all_routetable_data:
        router_exceptions = rename_net(all_routetable_data, ENTITY_NAMES.route_table, client)
    print("Route Table processing complete.")

    print("\nCollecting Internet Gateways data...")
    all_gateways_data = client.vpcs.internet_gateways.list()
    print("Gateway data collected. Processing Internet Gateways")
    if all_gateways_data:
        gateway_exceptions = rename_net(all_gateways_data, ENTITY_NAMES.gateway, client)
    print("Internet Gateway processing complete")

    print("\nCollecting DHCP Options Sets data...")
    all_dhcp_data = client.vpcs.dhcp_options.list()
    print("DHCP Options Sets data collected. Processing...")
    if all_dhcp_data:
        dhcp_exceptions = rename_net(all_dhcp_data, ENTITY_NAMES.dhcp, client)

    print("{}\n{}\n{}\n{}".format(vpc_exceptions,
                                  router_exceptions,
                                  gateway_exceptions,
                                  dhcp_exceptions))


def main():
    print('Initializing...\n\nPlease Note: Should you wish to specify custom names,'
          'you may do so by executing the custom_names.py script.\n\n')
    print('Creating client connection')
    client = create_symp_client()
    print('Select a task by entering the corresponding number.\n'
          'Rename to convention:\n'
          '\t1. All Network Entities.\n'
          '\t2. VPCs.\n'
          '\t3. Route Tables.\n'
          '\t4. Internet Gateways.\n'
          '\t5. DHCP Options Sets\n'
          '> ')
    switch = {
        1: 'rename_all(client)',
        2: """vpc_data = client.vpcs.list()
        rename_net(vpc_data, ENTITY_NAMES.vpc, client)""",
        3: """rt_data = client.vpcs.route_tables.list()
        rename_net(rt_data, ENTITY_NAMES.route_table, client)""",
        4: """gw_data = client.vpcs.internet_gateways.list()
        rename_net(gw_data, ENTITY_NAMES.gateway, client)""",
        5: """dhcp_data = client.vpcs.dhcp_options.list()
        rename_net(dhcp_data, ENTITY_NAMES.dhcp, client)"""
    }
    selection = validate.integer(5)
    exec (switch.get(selection))


class EntityNames:
    def __init__(self):
        def load_custom_names():
            root_path = os.path.dirname(os.path.abspath(__file__))
            try:
                with open('{}/resource/custom_entity_names.yml'.format(root_path)) as my_file:
                    try:
                        name_file = yaml.safe_load(my_file)
                    except yaml.YAMLError as yaml_exception:
                        print('Unable to load "{}/resource/custome_entity_names.yml".\nError: {}\n'
                              'Exiting...'.format(root_path, yaml_exception))
                        sys.exit()
            except IOError as io_error:
                print('Unable to open "{}/resource/config.yml".\n Error: {}\n'
                      'Exiting...'.format(root_path, io_error))
                sys.exit()
            return name_file

        def select_format():
            user_format = '{}_{}_{}'
            valid = False
            new_format = 0
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
                                       "\t6. project_domain_entity.type | dev_engineering_vpc")
                try:
                    new_format = int(new_format)
                    if 0 < new_format < 7:
                        valid = True
                except ValueError as value_error:
                    print('Invalid Input.\nError: {}'.format(value_error))
                    valid = False
            switcher = {
                1: '{0}_{1}_{2}',
                2: '{0}_{2}_{1}',
                3: '{1}_{0}_{2}',
                4: '{1}_{2}_{0}',
                5: '{2}_{0}_{1}',
                6: '{2}_{1}_{0}'
            }
            user_format = switcher.get(new_format, '{}_{}_{}')
            return user_format

        self.custom_names = load_custom_names()
        self.vpc = self.custom_names['vpc']
        self.route_table = self.custom_names['route_tables']
        self.gateway = self.custom_names['internet_gateways']
        self.dhcp = self.custom_names['dhcp_options_sets']
        self.style = select_format()


ENTITY_NAMES = EntityNames()

if __name__ == '__main__':
    sys.exit(main())