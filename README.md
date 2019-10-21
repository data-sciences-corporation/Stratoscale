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



# Stratoscale
Repository for scripts designed around Stratoscale's on-prem dev-ops/cloud/automation platform.
                                          INSTALLING THE SYMP CLIENT
Pull the client from a Stratoscale region and push it to your Python installation:
```
  sudo URL=https://<cluster_ip> bash -c "$(curl -k -sSL https://<cluster_ip>/install-client.sh)"
```
Export the client when running scripts that use it:
```
  export PYTHONPATH=/opt/symphony-client
```
