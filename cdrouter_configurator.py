import pandas as pd
import sys
from datetime import date
from cdrouter import CDRouter
from cdrouter.configs import Config

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
    "Users": {
        "parameter": "Users",
        "options": {"1": "SINGLE", "2": "MULTI"},
        "input_value": "SINGLE"
    },
    "IPv6": {
        "parameter": "IPv6",
        "options": {"1": "Yes", "2": "No"},
        "input_value": "Yes"
    }
}

#define a dict for the testvars
testvars = {

	"lan.lanClients":	"",
	"lan.lanInterface":	"",
	"lan2.lanBSSID":	"",
	"lan2.lanChannel":	"5GHz",
	"lan2.lanClients":	"1",
	"lan2.lanInterface":	"wifi0-acn",
	"lan2.lanSSID":		"",
    "lan2.wpaKey":		"",
    "lan3.lanBSSID":	"",
    "lan3.lanChannel":	"2.4GHz",
    "lan3.lanClients":	"1",
    "lan3.lanInterface":	"wifi1-ax",
    "lan3.lanSSID":		"",
    "lan3.wpaKey":		"",
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
for question_number, input_option in input_options.items():
    print(f"{input_option['parameter']}: {input_option['input_value']}")
print()


#set testvars for the DUT
DUT = input_options["DUT"]["input_value"]

column_DUT = DUT
DUT_dict = DUT_parameters_indexed.loc[:, column_DUT].to_dict()

testvars["RestartDut"] = "/home/qacafe/powercycle.tcl 192.168.200.210 " + DUT_dict["PDU"] + " cyber cyber"
testvars["lan.lanInterface"] = DUT_dict["LAN"]
testvars["lan2.lanSSID"] = DUT_dict["SSID-5G"]
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


config_name = "Python_"
config_name = config_name + input_options['DUT']['input_value'] + "_"
config_name = config_name + input_options['WAN Type']['input_value'] + "_"
config_name = config_name + input_options['WAN Mode']['input_value'] + "_"
config_name = config_name + input_options['Topology']['input_value'] + "_"
config_name = config_name + input_options['Users']['input_value'] + "_"
if input_options['IPv6']['input_value'] == "Yes":
    config_name = config_name + "IPv6"
if input_options['Reboot']['input_value'] == "No":
    config_name = config_name + " (NO REBOOT)"

print(config_name)

# generate the config file on CDRouter

base = "http://broadbandlab.ddns.net:81"
token = "d1b9f0dd"
# create service
c = CDRouter(base, token=token)

cfg = c.configs.create(Config(
    name=config_name + str(date.today()),
    contents=f"""

testvar RestartDut 	    	{testvars['RestartDut']} 
testvar lanInterface 		{testvars['lan.lanInterface']}
testvar lan.lanClients		{testvars['RestartDut']}
testvar lan.lanInterface	{testvars['lan.lanInterface']}
testvar lan2.lanBSSID		{testvars['lan2.lanBSSID']}
testvar lan2.lanChannel		{testvars['lan2.lanChannel']}
testvar lan2.lanClients		{testvars['lan2.lanClients']}
testvar lan2.lanInterface	{testvars['lan2.lanInterface']}
testvar lan2.lanSSID		{testvars['lan2.lanSSID']}
testvar lan2.wpaKey 		{testvars['lan2.wpaKey']}
testvar lan3.lanBSSID		{testvars['lan3.lanBSSID']}
testvar lan3.lanChannel		{testvars['lan3.lanChannel']}
testvar lan3.lanClients		{testvars['lan3.lanClients']}
testvar lan3.lanInterface	{testvars['lan3.lanInterface']}
testvar lan3.lanSSID		{testvars['lan3.lanSSID']}
testvar lan3.wpaKey		    {testvars['lan3.wpaKey']}
testvar pppoeUser	    	{testvars['pppoeUser']}
testvar pppoePassword		{testvars['pppoePassword']}
testvar RestartDutDelay		{testvars['RestartDutDelay']}
testvar wanInterface		{testvars['wanInterface']}
testvar wanMode		    	{testvars['wanMode']}
testvar wanVlanId		    {testvars['wanVlanId']}
testvar supportsIPv6		{testvars['supportsIPv6']}

#testvar_group.lan2	    	{testvars['RestartDut']}
#testvar_group.lan3  		{testvars['RestartDut']}

"""))

print('New config has ID {}'.format(cfg.id))

cfg_default = c.configs.get(1072)
print(cfg_default.name)
testvar_edit = cfg_default.edit_testvar(1072,wanVlanId)
print(testvar_edit)
