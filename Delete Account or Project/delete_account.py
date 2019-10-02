import sys
import time

import requests
from tabulate import tabulate

import resource.validate as validate_input
from delete_project import delete_project
from resource.symp_client import create_symp_client


def delete_account(account_id, client):
    print 'Deleting Account with ID: {}'.format(account_id)
    project_list = [project['id'] for project in client.projects.list() if project['domain_id'] == account_id]
    for project_id in project_list:
        delete_project(project_id, client)
    print 'All Projects Deleted. Disabling Account'
    disabled = False
    while not disabled:
        account_status = client.domains.get(account_id)['enabled']
        if account_status:
            client.domains.update(enabled=False, domain_id=account_id)
        else:
            disabled = True
            print 'Account Disabled. Deleting Account'
    deleted = False
    while not deleted:
        try:
            client.domains.delete(account_id)
        except requests.exceptions.HTTPError as delete_error:
            if '404' in str(delete_error):
                deleted = True
                print 'Account Deleted Successfully'


def get_all_account_data(client):
    data = client.domains.list()
    domain_data = [['#', 'Name', 'ID', 'Projects']]
    counter = 0
    for domain in data:
        counter += 1
        domain_name = domain['name']
        domain_id = domain['id']
        project_list_temp = [project['name'] for project in client.projects.list() if project['domain_id'] == domain_id]
        project_list = str()
        for project in project_list_temp:
            project_list = project_list + '{}, '.format(project)

        project_list = '[{}]'.format(project_list)
        if domain_id != 'default':
            domain_data.append([counter,
                                domain_name,
                                domain_id,
                                project_list])
        else:
            counter -= 1
    return domain_data


def main():
    name = 1
    id_position = 2
    confirmed = False
    print 'Creating client connection'
    client = create_symp_client()
    print 'Success\n\nCollecting Account Data'
    all_account_data = get_all_account_data(client)
    print 'Success'
    while not confirmed:
        print tabulate(all_account_data, headers="firstrow")
        print 'Please enter the number corresponding with the Account you wish to delete.'
        selected_account = validate_input.integer(len(all_account_data) - 1)
        print('Are you sure you wish to delete Account: {}?\n'
              'Enter "confirm" to continue'.format(all_account_data[selected_account][name]))
        confirmation = validate_input.confirmation()
        if confirmation:
            confirmed = True
        else:
            print('Unable to confirm.\n'
                  'Would you like to select a different account? [y/n]')
            select_different_account = validate_input.yes_no()
            if not select_different_account:
                sys.exit()
    start_time = time.time()
    delete_account(all_account_data[selected_account][id_position], client)


if __name__ == '__main__':
    sys.exit(main())
