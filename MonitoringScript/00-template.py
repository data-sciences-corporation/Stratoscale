#!/usr/bin/python3
########################################################################################################################
#                                           Stratoscale - Monitoring Script                                            #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# INTRODUCTION:                                                                                                        #
#   This script is part of a toolset which is being developed to help monitor and maintain a customer's                #
#   Stratoscale environment. It will monitor multiple components in the Stratoscale stack, which are otherwise         #
#   not monitored.                                                                                                     #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# MODULE DETAILS:                                                                                                      #
#   This module is for TODO: Fill in script explanation                                                                #
#                                                                                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#                                                                                                                      #
# CHANGELOG                                                                                                            #
# v0.1 - 18 December 2018 (Richard Raymond)                                                                            #
#   - Template                                                                                                         #
# v0.2 - 18 December 2018 (Richard Raymond)                                                                            #
#   - YAML Config file handling.                                                                                       #
#   - Added deeper error message customization (define error types in config.yaml)                                     #
# v0.3 - 19 December 2018 (Richard Raymond)                                                                            #
#   Source: 00-template.py [v0.3] - Requires: monitor.py [v0.4]                                                        #
#   - Added better directory & error handling (directories are defined in the config.yml                               #
# v0.4 - 22 March 2019 (Richard Raymond)                                                                               #
#   - Added currentstatus file, to allow for checking test results (improved e-mail granularity)                       #
# TODO vX.X - Date (Author)                                                                                            #
# TODO Source: 00-template.py [X.X] - Requires: monitor.py [vX.X]                                                      #
# TODO Changes between last build to this build                                                                        #
#                                                                                                                      #
########################################################################################################################

# MODULES
import sys
import yaml

# PARAMETERS
# 1 - Script name, 2 - Root path of calling script, 3 - Report filename

# CONFIG VARIABLES
rootpath = sys.argv[2]
config = yaml.load(open(rootpath + '/config.yml', 'r'))                     # Pull in config information from YML file.
johntestdirectory = rootpath + "/" + config['framework']['directory']['test'] + "/"        # Generate dir for test
reportdirectory = rootpath + "/" + config['framework']['directory']['report'] + "/"    # Generate dir for reports
workingdirectory = rootpath + "/" + config['framework']['directory']['working'] + "/"  # Generate dir for working dir
scriptdirectory = rootpath + "/" + config['framework']['directory']['script'] + "/"    # Generate dir for sub scripts

# SCRIPT VARIABLES
result = 0                                                                  # Initialize OK/NOK marker
error_message = "*UPDATE ME*"                                               # Error message to provide overview
test_data = "*UPDATE ME*"                                                   # Full error contents

# README.txt = scriptdirectory + sys.argv[1] + ".sh"                        # Create a script file
# ----------------------------------------------------------------------------------------------------------------------
# TODO - CUSTOM SCRIPT GOES HERE


# import ipdb; ipdb.set_trace()







# ----------------------------------------------------------------------------------------------------------------------
# UPDATE REPORT FILE
reportfile = open(reportdirectory + sys.argv[3] + '.txt', "a")              # Open the current report file
reportfile.write('TEST:         ' + sys.argv[1] + '\n')                     # Open test section in report file
reportfile.write('RESULT:       ' + config['framework']['errortypes'][result])  # Add test status to report
if result != 0:                                                             # Check if test wasn't successful
    errorfilename = sys.argv[3] + "_" + sys.argv[1]                         # Create a error_reportfile
    errorfile = open(reportdirectory + errorfilename + '.txt', "w+")        # Create error report file
    errorfile.write(test_data)                                              # Write error data to error file
    errorfile.close()                                                       # Close error file
    reportfile.write(" : " + error_message + '\n')                          # Add error message to report
    reportfile.write("\tPlease look at [" + errorfilename + ".txt] for further details.")
reportfile.write('\n' + config['framework']['formatting']['linebreak'] + '\n')  # Add line break to report file per test
reportfile.close()                                                          # Close report file
# ADD CURRENT TEST RESULT TO OVERALL REPORT STATUS
statusfile = open(rootpath + "/workingstatus", "r")
current_status = int(statusfile.read())
statusfile.close()
#import ipdb; ipdb.set_trace()
if current_status < result:
    statusfile = open(rootpath + "/workingstatus", "w")
    statusfile.truncate(0)
    statusfile.write(str(result))
    statusfile.close()
