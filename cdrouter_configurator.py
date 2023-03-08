import pandas as pd

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
    "WAN Protocol": {
        "parameter": "WAN Protocol",
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
        "options": {"1": "REBOOT", "2": "NO-REBOOT"},
        "input_value": "REBOOT"
    },
    "Users": {
        "parameter": "Users",
        "options": {"1": "SINGLE", "2": "MULTI"},
        "input_value": "SINGLE"
    },
    "IPv6": {
        "parameter": "IPv6",
        "options": {"1": "IPv6", "2": "IPv4"},
        "input_value": "IPv6"
    }
}

#define a dict for the testvars
testvars = {

	"lan.lanClients":	"32",
	"lan.lanInterface":	"GWMAC#1",
	"lan2.lanBSSID":	"APMAC#1",
	"lan2.lanChannel":	"5GHz",
	"lan2.lanClients":	"32",
	"lan2.lanInterface":	"wifi0-acn",
	"lan2.lanSSID":		"SSID#1",
    "lan2.wpaKey":		"WPA#1",
    "lan3.lanBSSID":	"APMAC#1",
    "lan3.lanChannel":	"2.4GHz",
    "lan3.lanClients":	"1",
    "lan3.lanInterface":	"wifi1-ax",
    "lan3.lanSSID":		"3",
    "lan3.wpaKey":		"WPA#2",
    "pppoeUser":		"0",
    "pppoePassword":	"0",
    "RestartDut":		"/home/qacafe/powercycle.tcl 192.168.200.210 eth6 cyber cyber",
    "RestartDutDelay":	"180",
    "testvar_group.lan2":	"0",
    "testvar_group.lan3":	"0",
    "wanInterface":		"GWMAC#2",
    "wanMode":	    	"DHCP",
    "wanVlanId":		"1000"

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
print(testvars["RestartDut"])

testvars["lan.lanInterface"] = DUT_dict["LAN"]
print(testvars["lan.lanInterface"])

testvars["lan2.lanSSID"] = DUT_dict["SSID-5G"]
print(testvars["lan2.lanSSID"])

testvars["lan2.lanBSSID"] = DUT_dict["AP-MAC-5G"]
print(testvars["lan2.lanBSSID"])

testvars["lan2.wpaKey"] = DUT_dict["WPA"]
print(testvars["lan2.wpaKey"])

testvars["lan3.lanBSSID"] = DUT_dict["AP-MAC-2G"]
print(testvars["lan3.lanBSSID"])

testvars["lan3.lanSSID"] = DUT_dict["SSID-2G"]
print(testvars["lan3.lanSSID"])

testvars["lan3.wpaKey"] = DUT_dict["WPA"]
print(testvars["lan3.wpaKey"])

testvars["lan3.lanChannel"] = DUT_dict["WPA"]
print(testvars["lan3.wpaKey"])



# set testvars for the WAN Type
WAN_Type = input_options["WAN Type"]["input_value"]

if WAN_Type == "VDSL":
    print(WAN_Type)
    testvars["wanInterface"] = "eth5"
    print(testvars["wanInterface"])

elif WAN_Type == "GE-WAN":
    print(WAN_Type)

    testvars["wanInterface"] = DUT_dict["GE-WAN"]
    print(testvars["wanInterface"])

else:
    print("ERROR")

