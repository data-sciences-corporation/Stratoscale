#!/usr/bin/env python3

# export PYTHONPATH=/opt/symphony-client/
import sys  # For running system level commands
import yaml  # For reading the config file
import os  # For path tools
import requests  # For symphony client
import symphony_client  # For connecting to Symphony region
import purestorage  # For running Pure Storage commands
from pip._vendor.distlib.compat import raw_input

rootpath = os.path.dirname(os.path.abspath(__file__))  # Get the root path


def create_symp_client(i_url, i_domain, i_username, i_password, i_project, i_insecure, i_cert_file=None):
    my_session = requests.Session()
    # disable Proxy
    my_session.trust_env = False
    if i_insecure is True:
        my_session.verify = False
    elif i_cert_file is not None:
        my_session.cert = i_cert_file
    sympclient = symphony_client.Client(url=i_url, session=my_session)
    sympclient.login(domain=i_domain, username=i_username, password=i_password,
                     project=i_project)
    return sympclient


# Import config file info
with open(rootpath + '/config.yml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        sys.exit()


# Run main program
print("*** Connecting to symphony to get DB information ***")

# 1. Create symp client connection
client = create_symp_client("https://" + config["region_access"]["ipaddress"],
                            config["region_access"]["cloud_admin"],
                            config["region_access"]["cloud_admin_user"],
                            config["region_access"]["cloud_admin_password"],
                            config["region_access"]["project"],
                            True,
                            None)
# 2. Ask for source and destination DBs
source_db_id = raw_input("\tPlease type the DB ID of the <source> database to proceed: ")
destination_db_id = raw_input("\tPlease type the DB ID of the <destination> database to proceed: ")
# source_db_id = "8d75b8e6-0a41-43b8-bb0a-787f81ed2537"
# destination_db_id = "28a5e294-0b7c-4943-9f6c-6e3ac12a11b3"
for db in client.dbs.instance.list():
    if db.get("id") == source_db_id:
        source_db = db
    if db.get("id") == destination_db_id:
        destination_db = db
try:
    print("\tSOURCE DB \tNAME [" + source_db.get("name") + "] \tIP ["
          + source_db.get("floating_ip") + "]")
    print("\tDESTINATION DB \tNAME [" + destination_db.get("name") + "] \tIP ["
          + destination_db.get("floating_ip") + "] \t<<< THIS DB's DATA WILL BE OVERWRITTEN !!!")
except:
    print("\tOne or more of the ID's provided was not found in this region [" +
          config["region_access"]["regionname"] + " - " + config["region_access"]["ipaddress"] +
          "].\n\tPlease confirm that these are the correct DB IDs.")
print("*** Validating environment ***")
if destination_db.get("status") != "Stopped":
    print(u"[\u2717] The DB is currently not in a stopped state.")
    answer = input("\tType PROCEEDANYWAY if you wish to overwrite the data: ")
    if answer != "PROCEEDANYWAY":
        sys.exit()
else:
    print(u"[\u2713] The destination DB is currently shut off.")

source = source_db.get("engine_revision_id")
destination = destination_db.get("engine_revision_id")
if source == destination:
    print(u"[\u2713] The DB's are using the same engine version revision..")
else:
    print(u"[\u2717] The DB's are not using the same engine version revision.")
    print("\tSource DB engine version revision\tID [{}]\n\tDestination DB engine version revision\tID [{}]".format(
        source_db.get("engine_revision_id"), destination_db("engine_revision_id")))
    sys.exit()
source = source_db.get("parameter_group_id")
destination = destination_db.get("parameter_group_id")
if source == destination:
    print(u"[\u2713] The DB's are using the same parameter group.")
else:
    print(u"[\u2717] The DB's parameter groups do not match. Please check your destination DB build.")
    print("\tSource DB parameter group\tID [{}]\n\tDestination DB parameter group\tID [{}]".format(
        source, destination))
    sys.exit()
try:
    source_volume_id = client.vms.get(source_db.get("vm_id")).get("volumes")[0]
    destination_volume_id = client.vms.get(destination_db.get("vm_id")).get("volumes")[0]
    print(u"[\u2713] DB data volumes identified as:\n\tSOURCE VOLUME [" + source_volume_id +
          "]\n\tDESTINATION VOLUME [" + destination_volume_id + "]")
except:
    print(u"[\u2717] One of the required Data Volumes is not found.")

# 4. Connect to Pure Storage array
pureip = str(config['purestoragearray']['ipaddress'])
puretoken = str(config['purestoragearray']['apitoken'])
array = purestorage.FlashArray(pureip, api_token=puretoken)
try:
    array_info = array.get()
    print(u"[\u2713] FlashArray {} [{}] (version {}) REST session established!".format(array_info['array_name'],
                                                                                pureip, array_info['version']))
except:
    print(u"[\u2717] Could not connect to the Pure Storage array - IP [" + pureip + "]")
    sys.exit()
# 5. List available snapshots
snapshots = array.get_volume("volume-" + source_volume_id + "-cinder", snap="True")
try:
    count = 0
    print(u"[\u2713] Snapshot/s exist for the source volume.")
    for snapshot in snapshots:
        count = count + 1
        print(" \t[{}]\t{} \t{} ".format(str(count), snapshot.get("created"), snapshot.get("name")))
except:
    print(u"[\u2717] There are no snapshots for the source volume.\n\tPlease check that it is protected.")
    sys.exit()
print("*** Select recovery point ***")
try:
    answer = input("\tPlease enter the number of the snapshot you'd like to restore data from: ")
    snapshot = snapshots[answer-1]
except:
    print("\tInvalid entry. Please try again.")
    sys.exit()
print("*** Updating data in destination DB ***")
print("\tData from [{}] ID [{}] at {} will be pushed into\n\t\t[{}] ID [{}]".format(
    source_db.get("name"), source_db_id, snapshot.get("created"), destination_db.get("name"), destination_db_id))
answer = raw_input("\tPlease type \"confirm\" to proceed: ").lower()
if answer == "confirm":
    array.copy_volume(snapshot.get("name"), "volume-{}-cinder".format(destination_volume_id), overwrite=True)
    print(u"[\u2713] The volume was successfully updated.")
    answer = raw_input("\tPlease type \"yes\" if you would like to start that DB now: ").lower()
    if answer == "yes":
        client.dbs.instance.start(destination_db_id)
else:
    print("Process Cancelled - Nothing will be done.")
# 7. End the Pure session and invalidate the cookie
array.invalidate_cookie()


#import ipdb; ipdb.set_trace()