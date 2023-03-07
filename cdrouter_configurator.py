import pandas as pd

DUT_parameters = pd.read_csv('DUT_parameters.csv')

# print(DUT_parameters.to_string())

#input_options

# Define a dict to store the questions and options
input_options = {
    "DUT": {
        "parameter": "Device Under Test",
        "options": {"1": "DUT#1", "2": "DUT#2", "3": "DUT#3", "4": "DUT#4"},
        "input_value": "DUT#1"
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

testvars = {
        "wanInterface": "eth5",
        "lanInterface": "eth2",
        "lanSSID": "eir1234567"
        }

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


WAN_Type = input_options["WAN Type"]["input_value"]

if WAN_Type == "VDSL":
    print(WAN_Type)
    testvars["wanInterface"] = "eth5"
    print(testvars["wanInterface"])

elif WAN_Type == "GE-WAN":
    print(WAN_Type)
    testvars["wanInterface"] = "eth2"
    print(testvars["wanInterface"])

else:
    print("ERROR")

