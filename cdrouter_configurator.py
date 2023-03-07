import pandas as pd

DUT_parameters = pd.read_csv('DUT_parameters.csv')

print(DUT_parameters.to_string())

#input_options

# Define a dict to store the questions and options
input_options = {
    "DUT": {
        "parameter": "Device Under Test",
        "options": {"1": "DUT#1", "2": "DUT#2", "3": "DUT#3", "4": "DUT#4"},
        "value": None
    },
    "WAN Type": {
        "parameter": "WAN Type",
        "options": {"1": "VDSL", "2": "GE-WAN/FTTH"},
        "value": None
    },
    "WAN Protocol": {
        "parameter": "WAN Protocol",
        "options": {"1": "DHCP", "2": "PPPoE"},
        "value": None
    },
    "Topology": {
        "parameter": "Topology",
        "options": {"1": "Gateway Only", "2": "Mesh"},
        "value": None
    },
    "Reboot": {
        "parameter": "Reboot or not",
        "options": {"1": "Reboot", "2": "No-reboot"},
        "value": None
    },
    "Users": {
        "parameter": "Users",
        "options": {"1": "Single", "2": "Multi"},
        "value": None
    },
    "IPv6": {
        "parameter": "IPv6",
        "options": {"1": "IPv6", "2": "IPv4"},
        "value": None
    }
}

# Loop through the questions and ask the user to select their answer

for question_number, input_options in input_options.items():
    question_text = input_options["parameter"]
    options = input_options["options"]
    
    print(question_text)
    for option_number, option_text in options.items():
        print(f"{option_number}. {option_text}")
    
    selected_option = input("Enter the number of your answer: ")
    input_options["value"] = options[selected_option]


# Print the questions and answers
print(input_options)
