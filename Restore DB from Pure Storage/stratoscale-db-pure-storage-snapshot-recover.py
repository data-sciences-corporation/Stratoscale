#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys  # For running system level commands
import yaml  # For reading the config file
import os  # For path tools
import requests  # For symphony client
import symphony_client  # For connecting to Symphony region
import purestorage  # For running Pure Storage commands
from pip._vendor.distlib.compat import raw_input
import datetime
from pytz import timezone
import pytz  # To add timezone to datetime


# In[2]:


#!{sys.executable} -m pip install purestorage
#!{sys.executable} -m pip install pyyaml


# In[3]:


print(u"[INIT] Initialising script.")
# Configure environment
tz_utc = pytz.timezone("UTC") # Set timezone for data source
current_day= ["ISO Week days start from 1","Mon","Tues","Wed","Thurs","Fri","Sat","Sun"]
rootpath = os.path.dirname(os.path.realpath('__file__'))  # Get the root path


# In[4]:


# Import config file data
with open(rootpath + '/config.yml', 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        print(u" [\u2713] Config file loaded.")
    except yaml.YAMLError as exc:
        print(u" [\u2717] Could not load the config file.")
        print(exc)
        exit()


# In[5]:


# Configure Stratoscale API connection
symp_url = "https://" + config["region_access"]["ipaddress"]
symp_domain = config["region_access"]["cloud_domain"]
symp_user = config["region_access"]["cloud_user"]
symp_password = config["region_access"]["cloud_password"]
symp_cloud_admin_password = config["region_access"]["cloud_admin_password"]
symp_project = config["region_access"]["project"],

my_session = requests.Session()
my_admin_session = requests.Session()
my_session.verify = False
my_admin_session.verify = False

try:
    client = symphony_client.Client(url=symp_url, session=my_session)
    client_login = client.login(domain=symp_domain, username=symp_user, password=symp_password,project=symp_project)
    print(u" [\u2713] Stratoscale user region [{}] session established.".format(symp_url))
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as user".format(symp_url))
    exit()

try:
    client_admin = symphony_client.Client(url=symp_url, session=my_admin_session)
    client_admin_login = client_admin.login(domain="cloud_admin", username="admin", password=symp_cloud_admin_password,project="default")
    print(u" [\u2713] Stratoscale cloud admin region [{}] session established.".format(symp_url))
except:
    print(u" [\u2717] Could not connect to the Stratosacle region [{}] as cloud admin".format(symp_url))
    exit()


# In[6]:


#Configure Pure Storage API Connection
pureip = str(config['purestoragearray']['ipaddress'])
puretoken = str(config['purestoragearray']['apitoken'])
array = purestorage.FlashArray(pureip, api_token=puretoken)
try:
    array_info = array.get()
    print(u" [\u2713] FlashArray {} [{}] (version {}) REST session established!".format(array_info['array_name'],
                                                                                pureip, array_info['version']))
except:
    print(u" [\u2717] Could not connect to the Pure Storage array - IP [" + pureip + "]")
    exit()


# In[7]:


try:
    dbs_id = raw_input("[>] Please input the database ID for the database you wish to recover a new DB from: ").lower()
    dbs_master_password = "NoPasswordRequired"
    #dbs_master_password = raw_input("[>] Please input the DB password: ")
    #dbs_id = "a5f089a9-e0f8-41aa-aba9-222e53005400"
except:
    print(u" [\u2717] Failed to collect the input data. Please try again.")
    exit()


# In[8]:


# Collect source DB data
print(u"[SOURCE DB] Collecting information from original DB [{}].".format(dbs_id))
database=client.dbs.instance.get(dbs_id)
# Environmentals
dbs_vpc_id = client.vpcs.list()[0].get("id")
print(u" [\u2713] VPC ID\t\t\t\t> {}".format(dbs_vpc_id))
dbs_storage_pool_id = client.melet.pools.get_default()
print(u" [\u2713] Storage Pool ID (Default)\t\t> {}".format(dbs_storage_pool_id))
# Get Database Metadata
dbs_original_name = database.get("name")
print(u" [\u2713] Source DB Name\t\t\t> {}".format(dbs_original_name))
dbs_engine_version_id = database.get("engine_version_id")
print(u" [\u2713] Source DB Engine Version ID\t> {}".format(dbs_engine_version_id))
dbs_network_id = database.get("network_id")
print(u" [\u2713] Source DB Network ID\t\t> {}".format(dbs_network_id))
dbs_master_username = database.get("master_user_name")
print(u" [\u2713] Source DB Master Username\t\t> {}".format(dbs_master_username))
dbs_master_db_name = database.get("db_name")
print(u" [\u2713] Source DB Master DB Name\t\t> {}".format(dbs_master_db_name))
dbs_instance_type = database.get("instance_type")
print(u" [\u2713] Source DB Instance Type\t\t> {}".format(dbs_instance_type))
dbs_project_id = database.get("project_id")
print(u" [\u2713] Source DB Instance Project ID\t> {}".format(dbs_project_id))
dbs_parameter_group_id = database.get("parameter_group_id")
print(u" [\u2713] Source DB Parameter Group ID\t> {}".format(dbs_parameter_group_id))
dbs_security_group_id = database.get("security_group_id")
print(u" [\u2713] Source DB Security Group ID\t> {}".format(dbs_security_group_id))
db_vm_data_vol_id = client.vms.get(database.vm_id).get("volumes")[0]
print(u" [\u2713] Source DB Volume ID\t\t> {}".format(db_vm_data_vol_id))


# In[9]:


# Get snapshots
print("[RECOVERY POINT] Identifying recovery/restore point for DB [{}].".format(dbs_id))
snapshots = array.get_volume("volume-" + db_vm_data_vol_id + "-cinder", snap="True")
try:
    count = 0
    print(u" [\u2713] Snapshot/s exist for the source volume.")
    for snapshot in snapshots:
        count = count + 1
        time_utc = datetime.datetime.strptime(snapshot.get("created"), "%Y-%m-%dT%H:%M:%SZ")
        time_utc = tz_utc.localize(time_utc, is_dst=None)
        snaptime = time_utc.astimezone(timezone("Africa/Johannesburg"))
        time = "{} [{}]".format(snaptime.strftime("%H:%M:%S %d/%m/%Y"),current_day[snaptime.isoweekday()])
        print(" [{}]\t{} \t{} ".format(str(count), time, snapshot.get("name")))
except:
    print(u"[\u2717] There are no snapshots for the source volume.\n\tPlease check that it is protected.")
    exit()


# In[10]:


# Select snapshot to deploy from
try:
    answer = input("[>] Please enter the number of the snapshot you'd like to restore data from: ")
    snapshot = snapshots[answer-1]
except:
    print(u" [\u2717] Invalid entry. Please try again.")
    sys.exit()
time_utc = datetime.datetime.strptime(snapshot.get("created"), "%Y-%m-%dT%H:%M:%SZ")
time_utc = tz_utc.localize(time_utc, is_dst=None)
snaptime = time_utc.astimezone(timezone("Africa/Johannesburg"))
time = "{} [{}]".format(snaptime.strftime("%H:%M:%S %d/%m/%Y"),current_day[snaptime.isoweekday()])
print(u" [\u2713] Snapshot to be used - [{}] - {}".format(answer, time))


# In[11]:


# Configuring parameters for new DB
print("[NEW DB DEPLOYMENT] Finalizing new DB.")
dbs_instance_name_new = "{}-recovery-{}".format(dbs_original_name,snaptime.strftime("%Y%m%d-%H%M"))
print(u" [\u2713] A new DB called [{}] will be created from data in the DB [{}] at {} ".format(
    dbs_instance_name_new,
    dbs_original_name,
    time
))
answer = raw_input("[>] Please type \"confirm\" to create the DB: ").lower()
if answer != "confirm":
    print(u" [\u2717] Process Cancelled - Nothing will be done.")
    exit()


# In[12]:


# Generating the data volume and import to Stratoscale
try:
    volumename = "temp_recovery_volume_{}".format(snaptime.strftime("%Y%m%d-%H%M"))
    response = array.copy_volume(snapshot.get("name"), volumename)
    print(u" [\u2713] Creating a volume from selected recovery point (snapshot) on the Pure Storage Array. NAME [{}]".format(volumename))
except:
    print(u" [\u2717] Could not create a volume from selected recovery point (snapshot) on the Pure Storage Array. Please try again.")
    exit()


# In[13]:


# Import volume for use in Stratoscale
try:
    response = client_admin.meletvolumes.manage(name="{} - Data".format(dbs_instance_name_new), 
                           storage_pool=dbs_storage_pool_id,
                           reference = {"name" : volumename},
                           description="A restored Data volume for {}".format(dbs_instance_name_new),
                           project_id=dbs_project_id
                          )
    volume_id = response.get("id")
    print(u" [\u2713] The volume [{}] was imported into Stratosacle and renamed to [{}]. ID [{}]".format(volumename, "{} - Data".format(dbs_instance_name_new), volume_id))
except:
    try:
        array.destroy_volume(volumename)
        array.eradicate_volume(volumename)
    except:
        print(u" [\u2717] Could not remove the volume. It may not ")
    print(u" [\u2717] Could not import the volume. Please try again.")
    exit()


# In[14]:


# Create a DB using the new data volume and existing settings.
try:
    response = client.dbs.instance.create(engine_version_id=dbs_engine_version_id,
                           name=dbs_instance_name_new,
                           storage_pool_id=dbs_storage_pool_id,
                           network_id=dbs_network_id,
                           master_user_name=dbs_master_username,
                           master_user_password=dbs_master_password,
                           sec_groups=dbs_security_group_id,
                           param_group_id=dbs_parameter_group_id,
                           instance_type=dbs_instance_type,
                           volume_id=volume_id,
                           is_external=True)
    print(u" [\u2713] The database [{}] has been started. Please log in to check status".format(dbs_instance_name_new))
except:
    print(u" [\u2717] The database [{}] could not be started.".format(dbs_instance_name_new))
    
    


# In[15]:


# Disconnect sessions
array.invalidate_cookie()

