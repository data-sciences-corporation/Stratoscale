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



# Data Sciences Corporation's Stratoscale script repository
Repository for scripts designed around Stratoscale's on-prem dev-ops/cloud/automation platform.

## Symp Client (Installation)
The Symp Client is required, when communicating to Stratoscale's own API. (Where possible, rather use the standard AWS calls, for max cloud compatibility).

Pull the client from a Stratoscale region and push it to your Python installation:
```bash
  sudo URL=https://<cluster_ip> bash -c "$(curl -k -sSL https://<cluster_ip>/install-client.sh)"
```
Export the client when running scripts that use it:
```bash
  export PYTHONPATH=/opt/symphony-client
```
Please note that this export is not permanent and should be run only when using the Symp client as it may cause errors with other Python related functions, such as 'pip install'.
