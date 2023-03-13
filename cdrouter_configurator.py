import pandas as pd
import sys
import time
from datetime import date
from cdrouter import CDRouter
from cdrouter.configs import Testvar
from cdrouter.configs import Config
from cdrouter.jobs import Job

# get the DUT parameters from the csv file
DUT_parameters = pd.read_csv('DUT_parameters.csv')
DUT_parameters_indexed = DUT_parameters.set_index('DUT')

# Define a dict to store the options
input_options = {
    "DUT": {
        "parameter": "DUT",
        "options": {"1": "DUT1", "2": "DUT2", "3": "DUT3", "4": "DUT4"},
        "input_value": "DUT1"
    },
    "WAN Type": {
        "parameter": "WAN Type",
        "options": {"1": "VDSL", "2": "GE-WAN"},
        "input_value": "VDSL"
    },
    "WAN Mode": {
        "parameter": "WAN Mode",
        "options": {"1": "DHCP", "2": "PPPoE"},
        "input_value": "DHCP"
    },
    "Topology": {
        "parameter": "Topology",
        "options": {"1": "GATEWAY", "2": "MESH"},
        "input_value": "GATEWAY"
    },
    "Reboot": {
        "parameter": "Reboot",
        "options": {"1": "Yes", "2": "No"},
        "input_value": "Yes"
    },
    "Clients": {
        "parameter": "Clients",
        "options": {"1": "LAN", "2": "WLAN(.11ac)", "3": "WLAN(.11ax)", "4": "MULTI"},
        "input_value": "1"
    },
    "IPv6": {
        "parameter": "IPv6",
        "options": {"1": "yes", "2": "no"},
        "input_value": "yes"
    }
}

#define a dict for the testvars
testvars = {

	"lan.lanClients":	"",
	"lan.lanInterface":	"",
	"lan.lanSSID":	"",
	"lan.lanSecurity":	"",
	"lan2.lanSecurity":	"",
	"lan3.lanSecurity":	"",
	"lan.wpaKey":	"",
	"lan.lanChannel":	"",
	"lan2.lanBSSID":	"",
	"lan2.lanChannel":	"5GHz",
	"lan2.lanClients":	"1",
	"lan2.lanInterface":	"wifi0-acn",
	"lan2.lanSSID":		"",
    "lan2.wpaKey":		"",
	"lan2.lanChannel":	"",
    "lan3.lanBSSID":	"",
    "lan3.lanChannel":	"2.4GHz",
    "lan3.lanClients":	"1",
    "lan3.lanInterface":	"wifi1-ax",
    "lan3.lanSSID":		"",
    "lan3.wpaKey":		"",
	"lan3.lanChannel":	"",
    "pppoeUser":		"",
    "pppoePassword":	"",
    "RestartDut":		"",
    "RestartDutDelay":	"180",
    "testvar_group.lan2":	"",
    "testvar_group.lan3":	"",
    "wanInterface":		"",
    "wanMode":	    	"DHCP",
    "wanVlanId":		"1000",
    "supportsIPv6":		""

        }

#get user input
for question_number, input_option in input_options.items():
    question_text = input_option["parameter"]
    options = input_option["options"]
    default_value = input_option["input_value"]
    
    print(question_text)
    for option_number, option_text in options.items():
        print(f"{option_number}. {option_text}")
   
    print("Default (1): " + default_value)
    selected_option = input(f"Select number or Enter for default: ")
    if len(selected_option) == 0 :
        selected_option = "1"

    print("Selected option " + str(selected_option) + " " + str(input_option["options"][selected_option]))
    print()
    input_option["input_value"] = input_option["options"][selected_option] 


# print parameter values
print("Selected Test Options:")
for question_number, input_option in input_options.items():
    print(f"{input_option['parameter']}: {input_option['input_value']}")
print()


#set testvars for the DUT
DUT = input_options["DUT"]["input_value"]

#column_DUT = DUT
DUT_dict = DUT_parameters_indexed.loc[:, DUT].to_dict()
#DUT_dict = DUT_parameters_indexed.loc[:, xxxcolumn_DUT].to_dict()

testvars["RestartDut"] = "/home/qacafe/powercycle.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"
testvars["lan.lanInterface"] = DUT_dict["LAN"]
testvars["lan2.lanSSID"] = DUT_dict["SSID-5G"]
testvars["lan.wpaKey"] = DUT_dict["WPA"]
testvars["lan2.lanBSSID"] = DUT_dict["AP-MAC-5G"]
testvars["lan2.wpaKey"] = DUT_dict["WPA"]
testvars["lan3.lanBSSID"] = DUT_dict["AP-MAC-2G"]
testvars["lan3.lanSSID"] = DUT_dict["SSID-2G"]
testvars["lan3.wpaKey"] = DUT_dict["WPA"]
testvars["lan3.lanChannel"] = DUT_dict["WPA"]
testvars["wanVlanId"] = DUT_dict["VLAN"]

# set testvars for the WAN Type
WAN_Type = input_options["WAN Type"]["input_value"]

if WAN_Type == "VDSL":
    testvars["wanInterface"] = "eth5"

elif WAN_Type == "GE-WAN":
    testvars["wanInterface"] = DUT_dict["GE-WAN"]

else:
    print("ERROR")

# set testvars for the WAN Protocol
testvars["wanMode"] = input_options["WAN Mode"]["input_value"]
testvars["supportsIPv6"] = input_options["IPv6"]["input_value"]

# set testvars for the reboot 
Reboot = input_options["Reboot"]["input_value"]

if Reboot == "No":
    testvars["RestartDut"] = ""

#set testvar for number of clients
Clients = input_options["Clients"]["input_value"]
if Clients == "LAN":
    testvars["lan.lanClients"] = "1"
    testvars["lan.lanSecurity"] = "NONE"
    testvars["lan2.lanInterface"] = "none"
    testvars["lan3.lanInterface"] = "none"
elif Clients == "WLAN(.11ac)":
    testvars["lan.lanInterface"] = "wifi0-acn"
    testvars["lan.lanChannel"] = "auto"
    testvars["lan.lanClients"] = "1"
    testvars["lan.lanSSID"] = DUT_dict["SSID-5G"]
    testvars["lan.wpaKey"] = DUT_dict["WPA"]
    testvars["lan.lanSecurity"] = "WPA"
    testvars["lan2.lanInterface"] = "none"
    testvars["lan3.lanInterface"] = "none"
elif Clients == "WLAN(.11ax)":
    testvars["lan.lanInterface"] = "wifi1-ax"
    testvars["lan.lanChannel"] = "auto"
    testvars["lan.lanClients"] = "1"
    testvars["lan.lanSSID"] = DUT_dict["SSID-5G"]
    testvars["lan.wpaKey"] = DUT_dict["WPA"]
    testvars["lan.lanSecurity"] = "WPA"
    testvars["lan2.lanInterface"] = "none"
    testvars["lan3.lanInterface"] = "none"
elif Clients == "MULTI":
    testvars["lan.lanInterface"] = DUT_dict["LAN"]
    testvars["lan.lanSecurity"] = "NONE"
    testvars["lan2.lanInterface"] = "wifi0-acn"
    testvars["lan3.lanInterface"] = "wifi1-ax"
    testvars["lan2.lanClients"] = "32"
    testvars["lan3.lanClients"] = "1"
    testvars["lan2.lanChannel"] = "5GHz"
    testvars["lan3.lanChannel"] = "2.4GHz"
    testvars["lan2.lanSSID"] = DUT_dict["SSID-5G"]
    testvars["lan3.lanSSID"] = DUT_dict["SSID-2G"]
    testvars["lan2.wpaKey"] = DUT_dict["WPA"]
    testvars["lan3.wpaKey"] = DUT_dict["WPA"]
    testvars["lan2.lanSecurity"] = "WPA"
    testvars["lan3.lanSecurity"] = "WPA"

# generate config name
config_name = "Python_"
config_name = config_name + DUT_dict['DESCRIPTION'] + "_" + DUT_dict['GW-FIRMWARE'] + "_"
#config_name = config_name + input_options['DUT']['input_value'] + "_"
config_name = config_name + input_options['WAN Type']['input_value'] + "_"
config_name = config_name + input_options['WAN Mode']['input_value'] + "_"
config_name = config_name + input_options['Topology']['input_value'] + "_"
config_name = config_name + input_options['Clients']['input_value']
if input_options['IPv6']['input_value'] == "yes":
    config_name = config_name + "_IPv6"
if input_options['Reboot']['input_value'] == "No":
    config_name = config_name + " (NO REBOOT)"

print(f"Generating config {config_name}")

# generate the config file on CDRouter

base = "http://broadbandlab.ddns.net:81"
token = "d1b9f0dd"

# connect to CDRouter
print("Connecting to CDRouter on " + base)
c = CDRouter(base, token=token)

# get default config
cfg_default = c.configs.get(1072)
#config_desc = cfg_default.description
config_notes = cfg_default.note

print("Updating config notes...")
config_notes = config_name + " - " + str(date.today()) + " - " +  config_notes
c.configs.edit(Config(id='1072', note=config_notes))

print("Updating testvars...")
c.configs.edit_testvar("1072", Testvar(name='wanInterface', value=testvars['wanInterface']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='wanMode', value=testvars['wanMode']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='RestartDut', value=testvars['RestartDut']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='supportsIPv6', value=testvars['supportsIPv6']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanInterface', value=testvars['lan.lanInterface']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanSSID', group='lan2', value=testvars['lan2.lanSSID']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanSSID', group='lan3', value=testvars['lan3.lanSSID']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='wpaKey', group='lan2', value=testvars['lan2.wpaKey']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='wpaKey', group='lan3', value=testvars['lan2.wpaKey']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanClients', group='lan2', value=testvars['lan2.lanClients']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanInterface', group='lan2', value=testvars['lan2.lanInterface']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanInterface', group='lan3', value=testvars['lan3.lanInterface']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='main', value=testvars['lan.lanSecurity']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='lan2', value=testvars['lan2.lanSecurity']))
print("...working...")
c.configs.edit_testvar("1072", Testvar(name='lanSecurity', group='lan3', value=testvars['lan3.lanSecurity']))


print("Finished updating testvars.")

print("Launching test package...")

print('Checking config for errors...')
pkg = c.packages.get(1056)
check = c.configs.check_config(cfg_default.contents)
if len(check.errors) > 0:
    print('config errors:'.format(pkg.name))
    for e in check.errors:
        print('        {0}'.format(e.error))
        print('')
        continue

# launch package
print('Launching package...')
j = c.jobs.launch(Job(package_id=1056))

# working for job to be assigned a result ID
while j.result_id is None:
    time.sleep(1)
    j = c.jobs.get(j.id)

print('        Result-ID: {0}'.format(j.result_id))
print('')
print(f"Package {pkg.name} launched!")
