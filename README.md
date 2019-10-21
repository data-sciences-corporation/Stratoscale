********************************************************************************************************
********************************************************************************************************
                                             !!! WARNING !!!
********************************************************************************************************
 PLEASE NOTE: THESE SCRIPTS ARE NOT ACTIVELY MAINTAINED. 
 IF YOU WISH TO USE ONE, PLEASE MAKE SURE TO COMMUNICATE WITH YOUR DATA SCIENCES CORP ENGINEER, 
 BEFORE USE IN PRODUCTION. AS CODE CHANGES OVER TIME, IT IS SAFEST TO CHECK THAT THE CODE IS VALID
 FOR THE CURRENT VERSION OF YOUR PLATFORM.
********************************************************************************************************
                                             !!! WARNING !!!
********************************************************************************************************
********************************************************************************************************


# Stratoscale
Repository for scripts designed around Stratoscale's on-prem dev-ops/cloud/automation platform.

********************************************************************************************************
                                          INSTALLING THE SYMP CLIENT
********************************************************************************************************
1. Run the following command:

  sudo URL=https://<cluster_ip> bash -c "$(curl -k -sSL https://<cluster_ip>/install-client.sh)"

In order to use the client:

  export PYTHONPATH=/opt/symphony-client
