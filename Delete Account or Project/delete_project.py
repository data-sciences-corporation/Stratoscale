"""
This script will delete all entities within a project
before deleting the project itself
"""

import sys
import time

import requests
from tabulate import tabulate

import resource.validate as validate_input
from resource.symp_client import create_symp_client


def delete_project(project_id, client):
    """
    Deletes all project elements and the project itself
    :param project_id: The ID of the project being deleted
    :param client: Symphony client session
    :return:
    """
    print 'Deleting Project with ID: {}\n'.format(project_id)

    print 'Deleting Elastic IPs'
    all_elastic_ip_ids = [elastic_ip['id'] for elastic_ip
                          in client.vpcs.elastic_ips.list(project_id=project_id)]
    for elastic_ip_id in all_elastic_ip_ids:
        deleted = False
        while not deleted:
            try:
                client.vpcs.elastic_ips.delete(elastic_ip_id)
            except requests.exceptions.HTTPError as elastic_e:
                if '404' in str(elastic_e):
                    deleted = True
    print 'Complete'

    print 'Deleting Load-Balancers'
    all_lb_ids = [lb['id'] for lb in client.lbaas.load_balancers.list()
                  if lb['project_id'] == project_id]
    for lb_id in all_lb_ids:
        deleted = False
        while not deleted:
            try:
                client.lbaas.load_balancers.delete(lb_id)
            except requests.exceptions.HTTPError as lb_e:
                if '404' in str(lb_e):
                    deleted = True
    print 'Complete'

    print 'Deleting Target Groups'
    all_tg_ids = [tg['id'] for tg in client.lbaas.target_groups.list()
                  if tg['project_id'] == project_id]
    for tg_id in all_tg_ids:
        deleted = False
        while not deleted:
            try:
                client.lbaas.target_groups.delete(tg_id)
            except requests.exceptions.HTTPError as tg_e:
                if '404' in str(tg_e):
                    deleted = True
    print 'Complete'

    print 'Deleting DB Instances'
    all_db_ids = [db['id'] for db in client.dbs.instance.list() if db['project_id'] == project_id]
    for db_id in all_db_ids:
        deleted = False
        while not deleted:
            try:
                client.dbs.instance.delete(db_id)
            except requests.exceptions.HTTPError as dbs_e:
                if '404' in str(dbs_e):
                    deleted = True
    print 'Completed'

    print 'Deleting DB Clusters'
    all_dbc_ids = [dbc['id'] for dbc in client.dbc.clusters.list()
                   if dbc['project_id'] == project_id]
    for dbc_id in all_dbc_ids:
        deleted = False
        while not deleted:
            try:
                client.dbc.clusters.delete(dbc_id)
            except requests.exceptions.HTTPError as dbc_e:
                if '404' in str(dbc_e):
                    deleted = True
    print 'Complete'

    print 'Deleting MapReduce Clusters'
    all_map_reduce_ids = [map_red_cluster['id'] for map_red_cluster
                          in client.mapreduce.clusters.list()
                          if map_red_cluster['project_id'] == project_id]
    for mr_cluster_id in all_map_reduce_ids:
        deleted = False
        while not deleted:
            try:
                client.mapreduce.clusters.delete(mr_cluster_id)
            except requests.exceptions.HTTPError as mr_e:
                if '404' in str(mr_e):
                    deleted = True
    print 'Completed'

    print 'Deleting Kubernetes Clusters'
    all_k8s_ids = [k8s_cluster['id'] for k8s_cluster in client.kubernetes.clusters.list()
                   if k8s_cluster['project_id'] == project_id]
    for k8s_id in all_k8s_ids:
        deleted = False
        while not deleted:
            try:
                client.kubernetes.clusters.delete(k8s_id)
            except requests.exceptions.HTTPError as k8s_e:
                if '404' in str(k8s_e):
                    deleted = True
    print 'Completed'

    print 'Deleting Auto-Scaling Groups'
    all_as_groups = [as_group['id'] for as_group in client.autoscaling_groups.groups.list()
                     if as_group['project_id'] == project_id]
    for asg_id in all_as_groups:
        deleted = False
        while not deleted:
            try:
                client.autoscaling_groups.groups.update(min_size=0, group_id=asg_id)
                client.autoscaling_groups.groups.update(desired_capacity=0, group_id=asg_id)
                client.autoscaling_groups.groups.delete(asg_id)
            except requests.exceptions.HTTPError as asg_e:
                if '404' in str(asg_e):
                    deleted = True
    print 'Completed'

    print 'Deleting Auto-Scaling Launch Configurations'
    all_launch_config_ids = [launch_config['id'] for launch_config in
                             client.autoscaling_groups.launch_configurations.list()
                             if launch_config['project_id'] == project_id]
    for launch_config_id in all_launch_config_ids:
        deleted = False
        while not deleted:
            try:
                client.autoscaling_groups.launch_configurations.delete(launch_config_id)
            except requests.exceptions.HTTPError as lc_e:
                if '404' in str(lc_e):
                    deleted = True
    print 'Completed'
    # print('Deleting Queueing Instances')
    print 'Deleting Notification Topics'
    all_topics_ids = [topic['id'] for topic in client.notification.topics.list()
                      if topic['project_id']]
    for topic_id in all_topics_ids:
        deleted = False
        while not deleted:
            try:
                client.notification.topics.delete(topic_id)
            except requests.exceptions.HTTPError as nt_e:
                if '404' in str(nt_e):
                    deleted = True
    print 'Completed'

    print 'Deleting Compute Rules'
    all_cr_ids = [rule['id'] for rule in client.compute_rules.list_compute_rules()
                  if rule['project-id'] == project_id]
    for rule_id in all_cr_ids:
        deleted = False
        while not deleted:
            try:
                client.compute_rules.delete_compute_rule(rule_id)
            except requests.exceptions.HTTPError as rule_e:
                if '404' in str(rule_e):
                    deleted = True
    print 'Completed'

    print 'Deleting Compute Instances'
    all_vm_data = [vm_data for vm_data in client.vms.list() if vm_data['project_id'] == project_id]
    for vm_instance in all_vm_data:
        managing_resource = vm_instance['managing_resource']
        if managing_resource['resource_type'] is None:
            client.vms.update(disable_delete=False, vm_id=vm_instance['id'])
            deleted = False
            while not deleted:
                try:
                    client.vms.stop(vm_instance['id'])
                except requests.exceptions.HTTPError as vm_e:
                    if '400' in str(vm_e):
                        refresh_data = client.vms.get(vm_instance['id'])
                        if refresh_data['status'] == 'shutoff':
                            client.vms.remove(vm_instance['id'])
                    if '404' in str(vm_e):
                        deleted = True
    print 'Completed'

    print 'Deleting VPC Peer Connections'
    all_peer_data = [peer for peer in client.vpcs.peering.list()]
    for peer_data in all_peer_data:
        if peer_data['status'] != 'deleted':
            requester = peer_data['requester_vpc_info']
            acceptor = peer_data['accepter_vpc_info']
            if requester['project_id'] == project_id or acceptor['project_id'] == project_id:
                client.vpcs.peering.delete(peer_data['id'])
    print 'Completed'

    print 'Deleting Network Interfaces'
    all_interface_ids = [interface['id'] for interface in client.vpcs.network_interfaces.list()
                         if interface['project_id'] == project_id]
    for interface_id in all_interface_ids:
        deleted = False
        while not deleted:
            try:
                client.vpcs.network_interfaces.delete(interface_id)
            except requests.exceptions.HTTPError as interface_e:
                if '404' in str(interface_e):
                    deleted = True
    print 'Completed'

    print 'Deleting VPC Subnets'
    all_subnet_ids = [subnet['id'] for subnet in client.vpcs.networks.list()
                      if subnet['project_id'] == project_id]
    for subnet_id in all_subnet_ids:
        deleted = False
        while not deleted:
            try:
                client.vpcs.networks.delete(subnet_id)
                client.vpcs.networks.get(subnet_id)
            except requests.exceptions.HTTPError as sub_e:
                if '404' in str(sub_e):
                    deleted = True
    print 'Completed'

    print 'Deleting VPC Security Groups'
    all_security_groups = [security_group for security_group in client.vpcs.security_groups.list()
                           if security_group['project_id'] == project_id]
    for security_group in all_security_groups:
        deleted = False
        while not deleted:
            try:
                client.vpcs.security_groups.delete_by_id(security_group['id'])
            except requests.exceptions.HTTPError as sec_e:
                if '404' in str(sec_e):
                    deleted = True
                if '400' in str(sec_e) and security_group['name'] == 'default':
                    print 'Skipping default Security Group'
                    deleted = True
    print 'Completed'

    print 'Deleting Gateways'
    all_gw_ids = [gateway['id'] for gateway in client.vpcs.internet_gateways.list()
                  if gateway['project_id'] == project_id]
    for gateway_id in all_gw_ids:
        deleted = False
        while not deleted:
            try:
                gateway_data = client.vpcs.internet_gateways.get(gateway_id)
                gateway_attachment_set = gateway_data['attachment_set']
                for attachment in gateway_attachment_set:
                    attached_vpc = attachment['vpc_id']
                    client.vpcs.internet_gateways.detach(internet_gateway_id=gateway_id, vpc_id=attached_vpc)
                client.vpcs.internet_gateways.delete(gateway_id)
            except requests.exceptions.HTTPError as gw_e:
                if '404' in str(gw_e):
                    deleted = True
    print 'Completed'

    print 'Deleting NAT Gateways'
    all_nat_ids = [nat['id'] for nat in client.vpcs.nat_gateways.list()
                   if nat['project_id'] == project_id]
    for nat_id in all_nat_ids:
        deleted = False
        while not deleted:
            try:
                client.vpcs.nat_gateways.delete(nat_id)
            except requests.exceptions.HTTPError as nat_e:
                if '404' in str(nat_e):
                    deleted = True
    print 'Completed'

    print 'Deleting VPCs'
    all_vpc_ids = [vpc['id'] for vpc in client.vpcs.list() if vpc['project_id'] == project_id]
    for vpc_id in all_vpc_ids:
        deleted = False
        while not deleted:
            try:
                client.vpcs.delete(vpc_id)
            except requests.exceptions.HTTPError as vpc_e:
                if '404' in str(vpc_e):
                    deleted = True
    print 'Completed'

    print 'Deleting DHCP Options'
    all_dhcp_ids = [dhcp['id'] for dhcp in client.vpcs.dhcp_options.list()
                    if dhcp['project_id'] == project_id]
    for dhcp_id in all_dhcp_ids:
        deleted = False
        while not deleted:
            try:
                client.vpcs.dhcp_options.delete(dhcp_id)
            except requests.exceptions.HTTPError as dhcp_e:
                if '404' in str(dhcp_e):
                    deleted = True
    print 'Completed'

    print 'Deleting Volumes'
    all_volume_ids = [volume['id'] for volume in client.meletvolumes.list() if volume['projectID'] == project_id]
    for volume_id in all_volume_ids:
        client.meletvolumes.remove(volume_id)
    print 'Completed'

    print 'Deleting Project'
    client.projects.delete(project_id)
    print 'Complete'


def get_all_project_data(client):
    """
    Uses the symphony client session to obtain all project data
    and return a tabulate-able list
    :param client: Symphony Client session
    :return: Relevant data of all projects on cluster
    """
    data = client.projects.list()
    project_data = [['#', 'ID', 'Name', 'Enabled', 'Domain Name', 'Domain ID']]
    number = 0
    for project in data:
        number += 1
        project_id = project['id']
        project_enabled = project['enabled']
        project_name = project['name']
        project_domain_name = project['domain_name']
        project_domain_id = project['domain_id']
        if project_domain_id != 'default':
            project_data.append([number,
                                 project_id,
                                 project_name,
                                 project_enabled,
                                 project_domain_name,
                                 project_domain_id])
        else:
            number -= 1
    return project_data


def main():
    """
    Main function to allow user to select a project to delete
    :return:
    """
    project_id = 1
    name = 2
    confirmed = False
    print 'Creating client connection...'
    client = create_symp_client()
    print 'Success!'
    print '\nCollecting project data...'
    all_project_data = get_all_project_data(client)
    print 'Success!'
    while not confirmed:
        print tabulate(all_project_data, headers="firstrow")
        print 'Please enter the number corresponding with the project you wish to delete.'
        selected_project = validate_input.integer(len(all_project_data)-1)
        print('Are you sure you wish to delete Project: {}?\n'
              'Enter "confirm" to continue'.format(all_project_data[selected_project][name]))
        confirmation = validate_input.confirmation()
        if confirmation:
            confirmed = True
        else:
            print('Unable to confirm.\n'
                  'Would you like to select a different project? [y/n]')
            select_different_project = validate_input.yes_no()
            if not select_different_project:
                sys.exit()
    start_time = time.time()
    delete_project(all_project_data[selected_project][project_id], client)
    end_time = time.time()
    duration = end_time - start_time
    print 'Delete Complete.\nRuntime was {} seconds.'.format(duration)


if __name__ == '__main__':
    sys.exit(main())
