from flask import Flask, render_template, request
from flask_basicauth import BasicAuth
import pandas as pd
import sys
import time
import logging
from datetime import date
from flask import jsonify
from cdrouter import CDRouter
from cdrouter.configs import Testvar
from cdrouter.configs import Config
from cdrouter.jobs import Job
from cdrouter.devices import Device
from cdrouter.packages import Package

logging.basicConfig(filename='cdrouter.log', level=logging.DEBUG)

# get the DUT parameters from the csv file
print(f"Getting DUT parameters from file...")
DUT_parameters = pd.read_csv('~/CDROUTER_CONFIGURATOR/cdrouter_DUT.csv')
DUT_parameters_indexed = DUT_parameters.set_index('DUT')

# get the CLIENT parameters from the csv file
print(f"Getting CLIENT parameters from file...")
CLIENT_parameters = pd.read_csv('~/CDROUTER_CONFIGURATOR/cdrouter_CLIENTS.csv')
CLIENT_parameters_indexed = CLIENT_parameters.set_index('CLIENT')

# create the web page
app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'bblab'
app.config['BASIC_AUTH_PASSWORD'] = 'e1rc0mbblab'
app.config['BASIC_AUTH_FORCE'] = True

app.logger.debug("debug log info")
app.logger.info("Info log information")
app.logger.warning("Warning log info")
app.logger.error("Error log info")
app.logger.critical("Critical log info")

basic_auth = BasicAuth(app)

# Define a dict to store the DUT options
print(f"Defining options dict...")
options = { 
        "DUT": {"1": "DUT1", "2": "DUT2", "3": "DUT3", "4": "DUT4", "5": "DUT5", "6": "DUT6"},
        "WAN Type": {"1": "VDSL", "2": "GE-WAN"},
        "WAN Mode": {"1": "DHCP", "2": "PPPoE"},
        "Topology": {"1": "GATEWAY", "2": "MESH"},
        "Reboot": {"1": "yes", "2": "no"},
        "TR-069": {"1": "no", "2": "yes"},
        "Clients": {"1": "LAN", "2": "WiFi4 (2.4GHz)", "3": "WiFi5 (5GHz)", "4": "WiFi6 (2.4GHz)",  "5": "WiFi6 (5GHz)", "6": "WiFi6e (6GHz)", "7": "WiFi7 (MLO)", "9": "MULTI"},
        "IPv6": {"1": "yes", "2": "no"}, 
        "Package": {"1": "Base", "2": "Sanity", "3": "Security", "4": "Performance/Stability", "5": "DOS", "6": "Performance", "7": "Mgmt: TR-069"} 
        }

print(f"Waiting for form to be posted...")

@app.route('/cdrouter_configurator', methods=['GET', 'POST'])
@basic_auth.required
def cdrouter_configurator_test():
    if request.method == 'POST' :
        selected_options=request.form

# Connect to CDRouter
        base = sys.argv[1]
        token = sys.argv[2]

        print(f"Opening connection to CDRouter {base} with token {token}...")
        c = CDRouter(base, token=token)

# Get default config
        print(f"Geting Config ID 3471 name...")
        cfg_default = c.configs.get(3471)
        print(f" Config 3471 is named {cfg_default.name}...")

# Define a dict to store basic testvars
        print(f"Defining testvars_basic dict...")
        testvars_basic = {
        "supportsIPv6": Testvar(name='supportsIPv6', group='main', value='yes'),
        "RestartDut": Testvar(name='RestartDut', group='main', value=''),
        "RestartDutDelay": Testvar(name='RestartDutDelay', group='main', value='30'),
        }

# Define a dict to store WAN testvars
        print(f"Defining testvars_wan dict...")
        testvars_wan = {
        "wanMode": Testvar(name='wanMode', group='main', value='DHCP'),
        "wanInterface": Testvar(name='wanInterface', group='main', value='eth9-10G'),
        "wanVlanId": Testvar(name='wanVlanId', group='main', value='10'),
        "pppoeUser": Testvar(name='pppoeUser', group='main', value='eircom@eircom.net'),
        "pppoePassword": Testvar(name='pppoePassword', group='main', value='broadband1')
        }

# Define a dict to store CWMP/ACS testvars
        print(f"Defining testvars_acs dict...")
        testvars_acs = {
        "supportsCWMP": Testvar(name='supportsCWMP', group='main', value=''),
        "tr69DownloadImage": Testvar(name='tr69DownloadImage', group='main', value=''),
        "tr69DownloadOriginalImage": Testvar(name='tr69DownloadOriginalImage', group='main', value=''),
        "acsDefaultUser": Testvar(name='acsDefaultUser', group='main', value='')
        }

# Define a dict to store LAN testvars (LAN groups 1-8)
        print(f"Defining testvars_acs dict...")
        testvars_lan = {
        "lan.lanInterface": Testvar(name='lanInterface', group='main', value='none'),
        "lan2.lanInterface": Testvar(name='lanInterface', group='lan2', value='none'),
        "lan3.lanInterface": Testvar(name='lanInterface', group='lan3', value='none'),
        "lan4.lanInterface": Testvar(name='lanInterface', group='lan4', value='none'),
        "lan5.lanInterface": Testvar(name='lanInterface', group='lan5', value='none'),
        "lan6.lanInterface": Testvar(name='lanInterface', group='lan6', value='none'),
        "lan7.lanInterface": Testvar(name='lanInterface', group='lan7', value='none'),
        "lan8.lanInterface": Testvar(name='lanInterface', group='lan8', value='none'),
        "lan.lanSecurity": Testvar(name='lanSecurity', group='main', value='NONE'),
        "lan2.lanSecurity": Testvar(name='lanSecurity', group='lan2', value='NONE'),
        "lan3.lanSecurity": Testvar(name='lanSecurity', group='lan3', value='NONE'),
        "lan4.lanSecurity": Testvar(name='lanSecurity', group='lan4', value='NONE'),
        "lan5.lanSecurity": Testvar(name='lanSecurity', group='lan5', value='NONE'),
        "lan6.lanSecurity": Testvar(name='lanSecurity', group='lan6', value='NONE'),
        "lan7.lanSecurity": Testvar(name='lanSecurity', group='lan7', value='NONE'),
        "lan8.lanSecurity": Testvar(name='lanSecurity', group='lan8', value='NONE'),
        "lan.lanChannel": Testvar(name='lanChannel', group='main', value='auto'),
        "lan2.lanChannel": Testvar(name='lanChannel', group='lan2', value='auto'),
        "lan3.lanChannel": Testvar(name='lanChannel', group='lan3', value='auto'),
        "lan4.lanChannel": Testvar(name='lanChannel', group='lan4', value='auto'),
        "lan5.lanChannel": Testvar(name='lanChannel', group='lan5', value='auto'),
        "lan6.lanChannel": Testvar(name='lanChannel', group='lan6', value='auto'),
        "lan7.lanChannel": Testvar(name='lanChannel', group='lan7', value='auto'),
        "lan8.lanChannel": Testvar(name='lanChannel', group='lan8', value='auto'),
        "lan.lan80211Phy": Testvar(name='lan80211Phy', group='main', value='auto'),
        "lan2.lan80211Phy": Testvar(name='lan80211Phy', group='lan2', value='auto'),
        "lan3.lan80211Phy": Testvar(name='lan80211Phy', group='lan3', value='auto'),
        "lan4.lan80211Phy": Testvar(name='lan80211Phy', group='lan4', value='auto'),
        "lan5.lan80211Phy": Testvar(name='lan80211Phy', group='lan5', value='auto'),
        "lan6.lan80211Phy": Testvar(name='lan80211Phy', group='lan6', value='auto'),
        "lan7.lan80211Phy": Testvar(name='lan80211Phy', group='lan7', value='auto'),
        "lan8.lan80211Phy": Testvar(name='lan80211Phy', group='lan8', value='auto'),
        "lan.lanClients": Testvar(name='lanClients', group='main', value='1'),
        "lan2.lanClients": Testvar(name='lanClients', group='lan2', value='1'),
        "lan3.lanClients": Testvar(name='lanClients', group='lan3', value='1'),
        "lan4.lanClients": Testvar(name='lanClients', group='lan4', value='1'),
        "lan5.lanClients": Testvar(name='lanClients', group='lan5', value='1'),
        "lan6.lanClients": Testvar(name='lanClients', group='lan6', value='1'),
        "lan7.lanClients": Testvar(name='lanClients', group='lan7', value='1'),
        "lan8.lanClients": Testvar(name='lanClients', group='lan8', value='1'),
        "lan.lanSSID": Testvar(name='lanSSID', group='main', value=''),
        "lan2.lanSSID": Testvar(name='lanSSID', group='lan2', value=''),
        "lan3.lanSSID": Testvar(name='lanSSID', group='lan3', value=''),
        "lan4.lanSSID": Testvar(name='lanSSID', group='lan4', value=''),
        "lan5.lanSSID": Testvar(name='lanSSID', group='lan5', value=''),
        "lan6.lanSSID": Testvar(name='lanSSID', group='lan6', value=''),
        "lan7.lanSSID": Testvar(name='lanSSID', group='lan7', value=''),
        "lan8.lanSSID": Testvar(name='lanSSID', group='lan8', value=''),
        "lan.lanBSSID": Testvar(name='lanBSSID', group='main', value=''),
        "lan2.lanBSSID": Testvar(name='lanBSSID', group='lan2', value=''),
        "lan3.lanBSSID": Testvar(name='lanBSSID', group='lan3', value=''),
        "lan4.lanBSSID": Testvar(name='lanBSSID', group='lan4', value=''),
        "lan5.lanBSSID": Testvar(name='lanBSSID', group='lan5', value=''),
        "lan6.lanBSSID": Testvar(name='lanBSSID', group='lan6', value=''),
        "lan7.lanBSSID": Testvar(name='lanBSSID', group='lan7', value=''),
        "lan8.lanBSSID": Testvar(name='lanBSSID', group='lan8', value=''),
        "lan.wpaKey": Testvar(name='wpaKey', group='main', value=''),
        "lan2.wpaKey": Testvar(name='wpaKey', group='lan2', value=''),
        "lan3.wpaKey": Testvar(name='wpaKey', group='lan3', value=''),
        "lan4.wpaKey": Testvar(name='wpaKey', group='lan4', value=''),
        "lan5.wpaKey": Testvar(name='wpaKey', group='lan5', value=''),
        "lan6.wpaKey": Testvar(name='wpaKey', group='lan6', value=''),
        "lan7.wpaKey": Testvar(name='wpaKey', group='lan7', value=''),
        "lan8.wpaKey": Testvar(name='wpaKey', group='lan8', value=''),
        "lan.wpaMode": Testvar(name='wpaMode', group='main', value='auto'),
        "lan2.wpaMode": Testvar(name='wpaMode', group='lan2', value='auto'),
        "lan3.wpaMode": Testvar(name='wpaMode', group='lan3', value='auto'),
        "lan4.wpaMode": Testvar(name='wpaMode', group='lan4', value='auto'),
        "lan5.wpaMode": Testvar(name='wpaMode', group='lan5', value='auto'),
        "lan6.wpaMode": Testvar(name='wpaMode', group='lan6', value='auto'),
        "lan7.wpaMode": Testvar(name='wpaMode', group='lan7', value='auto'),
        "lan8.wpaMode": Testvar(name='wpaMode', group='lan8', value='auto'),
        "lan.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='main', value='auto'),
        "lan2.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='lan2', value='auto'),
        "lan3.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='lan3', value='auto'),
        "lan4.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='lan4', value='auto'),
        "lan5.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='lan5', value='auto'),
        "lan6.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='lan6', value='auto'),
        "lan7.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='lan7', value='auto'),
        "lan8.wpaKeyMgmt": Testvar(name='wpaKeyMgmt', group='lan8', value='auto'),
        "lan.wpaCipher": Testvar(name='wpaCipher', group='main', value='auto'),
        "lan2.wpaCipher": Testvar(name='wpaCipher', group='lan2', value='auto'),
        "lan3.wpaCipher": Testvar(name='wpaCipher', group='lan3', value='auto'),
        "lan4.wpaCipher": Testvar(name='wpaCipher', group='lan4', value='auto'),
        "lan5.wpaCipher": Testvar(name='wpaCipher', group='lan5', value='auto'),
        "lan6.wpaCipher": Testvar(name='wpaCipher', group='lan6', value='auto'),
        "lan7.wpaCipher": Testvar(name='wpaCipher', group='lan7', value='auto'),
        "lan8.wpaCipher": Testvar(name='wpaCipher', group='lan8', value='auto'),
        "lan.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='main', value='auto'),
        "lan2.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='lan2', value='auto'),
        "lan3.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='lan3', value='auto'),
        "lan4.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='lan4', value='auto'),
        "lan5.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='lan5', value='auto'),
        "lan6.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='lan6', value='auto'),
        "lan7.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='lan7', value='auto'),
        "lan8.wpaGroupCipher": Testvar(name='wpaGroupCipher', group='lan8', value='auto')
         }

# Get the parameters for the selected DUT
        DUT = selected_options["DUT"]
        DUT_dict = DUT_parameters_indexed.loc[:, DUT].to_dict()
        DUT_BANDS = DUT_dict["BANDS"]

# Get the parameters for the selected client
        CLIENT = selected_options["Clients"]
        CLIENT_dict = CLIENT_parameters_indexed.loc[:, CLIENT].to_dict()

# Update the WAN VLAN
        testvars_wan["wanVlanId"].value = DUT_dict["VLAN"]
        testvars_acs["acsDefaultUser"].value = DUT_dict["GW-OUI"] + "-" + DUT_dict["GW-SERIAL"]

#create tag list
        tag_list = list()
        tag_list.append("python")
        tag_list.append(DUT_dict["GW-NAME"])

# set testvars for the selected WAN Type
        WAN_Type = selected_options["WAN Type"]

        if WAN_Type == "VDSL":
            testvars_wan["wanInterface"].value = "eth5"
# shutdown all CPE and the WAN switch and start the DUT and DSLAM
            testvars_basic["RestartDut"].value = "/home/qacafe/CDROUTER_POWERCYCLE/powercycle_VDSL.tcl 192.168.88.105 " + DUT_dict["PDU"] + " cyber cyber"
            testvars_basic["RestartDutDelay"].value = 180
            testvars_wan["wanVlanId"].value = 1000
            tag_list.append("VDSL")
        elif WAN_Type == "GE-WAN":
            testvars_wan["wanInterface"].value = DUT_dict["GE-WAN"]
# shutdown all CPE and DSLAM and start the DUT and the WAN switch
#            testvars_basic["RestartDut"].value = "/home/qacafe/CDROUTER_POWERCYCLE/RGWResetServer.tcl " + DUT_dict["PDUv2"]
            testvars_basic["RestartDutDelay"].value = 90
            testvars_wan["wanVlanId"].value = 10
            tag_list.append("FTTH")
        else:
            print("ERROR")

# set testvars for the selected WAN mode (DHCP/PPPoE)
        testvars_wan["wanMode"].value = selected_options["WAN Mode"]
        tag_list.append(testvars_wan["wanMode"].value)

# set testvars for ACS/CWMP
        testvars_acs["supportsCWMP"].value = selected_options["TR-069"]
        tr69_option = selected_options["TR-069"]
        if tr69_option == "yes":
            testvars_acs["tr69DownloadImage"].value = "/home/qacafe/FIRMWARES" + DUT_dict["GW-FW-MIRROR"]
            testvars_acs["tr69DownloadOriginalImage"].value = "/home/qacafe/FIRMWARES" + DUT_dict["GW-FW-IMAGE"]
            tag_list.append("CWMP")

# set testvars for IPv6
        testvars_basic["supportsIPv6"].value = selected_options["IPv6"]

# set testvars for reboot
        Reboot = selected_options["Reboot"]

        if Reboot == "no":
            testvars_basic["RestartDut"].value = ""
            testvars_basic["RestartDutDelay"].value = 60
        elif Reboot == "quick":
            testvars_basic["RestartDut"].value = "/home/qacafe/CDROUTER_POWERCYCLE/powercycle_QUICK.tcl 192.168.88.105 " + DUT_dict["PDU"] + " cyber cyber"
        elif Reboot == "yes":
            print(f"Device will be rebooted using the relay board {DUT_dict['PDUv2']} ...")
            testvars_basic["RestartDut"].value = "/home/qacafe/CDROUTER_POWERCYCLE/RGWResetServer_ALLOFF_ON.tcl " + DUT_dict["PDUv2"]

# Set testvars for the selected client
        Clients = selected_options["Clients"]


        if Clients == "LAN":
            print(f"Using LAN Client ...")
            testvars_lan["lan.lanInterface"].value  = CLIENT_dict["lanInterface"]
            testvars_lan["lan.lanSecurity"].value  = CLIENT_dict["lanSecurity"]
            testvars_lan["lan.lanClients"].value  = "1"
            
            tag_list.append("LAN")

        elif Clients == "WiFi4 (2.4GHz)":
            print(f"Using WiFi4 (2.4GHz)  Client ...")
            
            testvars_lan["lan.lanSSID"].value  = DUT_dict["SSID-2G"]
            testvars_lan["lan.wpaKey"].value  = DUT_dict["WPA"]

            testvars_lan["lan.lanInterface"].value  = CLIENT_dict["lanInterface"]
            testvars_lan["lan.lanSecurity"].value  = CLIENT_dict["lanSecurity"]
            testvars_lan["lan.lanClients"].value  = "1"
            testvars_lan["lan.lanChannel"].value  = CLIENT_dict["lanChannel"]
            testvars_lan["lan.lan80211Phy"].value  = CLIENT_dict["lan80211Phy"]
            testvars_lan["lan.wpaKeyMgmt"].value  = CLIENT_dict["wpaKeyMgmt"]
            testvars_lan["lan.wpaCipher"].value  = CLIENT_dict["wpaCipher"]
            testvars_lan["lan.wpaGroupCipher"].value  = CLIENT_dict["wpaGroupCipher"]
            testvars_lan["lan.wpaMode"].value  = CLIENT_dict["wpaMode"]
            
            tag_list.append("WLAN")
            tag_list.append("WiFi4")
            tag_list.append("2.4GHz")

        elif Clients == "WiFi5 (5GHz)":
            print(f"Using WiFi5 (5GHz)  Client ...")

            testvars_lan["lan.lanSSID"].value  = DUT_dict["SSID-5G"]
            testvars_lan["lan.wpaKey"].value  = DUT_dict["WPA"]

            testvars_lan["lan.lanInterface"].value  = CLIENT_dict["lanInterface"]
            testvars_lan["lan.lanSecurity"].value  = CLIENT_dict["lanSecurity"]
            testvars_lan["lan.lanClients"].value  = "1"
            testvars_lan["lan.lanChannel"].value  = CLIENT_dict["lanChannel"]
            testvars_lan["lan.lan80211Phy"].value  = CLIENT_dict["lan80211Phy"]
            testvars_lan["lan.wpaKeyMgmt"].value  = CLIENT_dict["wpaKeyMgmt"]
            testvars_lan["lan.wpaCipher"].value  = CLIENT_dict["wpaCipher"]
            testvars_lan["lan.wpaGroupCipher"].value  = CLIENT_dict["wpaGroupCipher"]

            tag_list.append("WLAN")
            tag_list.append("WiFi5")
            tag_list.append("5GHz")

        elif Clients == "WiFi6 (2.4GHz)":
            print(f"Using WiFi6 (2.4GHz)  Client ...")
            
            testvars_lan["lan.lanSSID"].value  = DUT_dict["SSID-2G"]
            testvars_lan["lan.wpaKey"].value  = DUT_dict["WPA"]

            testvars_lan["lan.lanInterface"].value  = CLIENT_dict["lanInterface"]
            testvars_lan["lan.lanSecurity"].value  = CLIENT_dict["lanSecurity"]
            testvars_lan["lan.lanClients"].value  = "1"
            testvars_lan["lan.lanChannel"].value  = CLIENT_dict["lanChannel"]
            testvars_lan["lan.lan80211Phy"].value  = CLIENT_dict["lan80211Phy"]
            testvars_lan["lan.wpaKeyMgmt"].value  = CLIENT_dict["wpaKeyMgmt"]
            testvars_lan["lan.wpaCipher"].value  = CLIENT_dict["wpaCipher"]
            testvars_lan["lan.wpaGroupCipher"].value  = CLIENT_dict["wpaGroupCipher"]
            
            tag_list.append("WLAN")
            tag_list.append("WiFi6")
            tag_list.append("2.4GHz")

        elif Clients == "WiFi6 (5GHz)":
            print(f"Using WiFi6 (5GHz)  Client ...")

            testvars_lan["lan.lanSSID"].value  = DUT_dict["SSID-5G"]
            testvars_lan["lan.wpaKey"].value  = DUT_dict["WPA"]

            testvars_lan["lan.lanInterface"].value  = CLIENT_dict["lanInterface"]
            testvars_lan["lan.lanSecurity"].value  = CLIENT_dict["lanSecurity"]
            testvars_lan["lan.lanClients"].value  = "1"
            testvars_lan["lan.lanChannel"].value  = CLIENT_dict["lanChannel"]
            testvars_lan["lan.lan80211Phy"].value  = CLIENT_dict["lan80211Phy"]
            testvars_lan["lan.wpaKeyMgmt"].value  = CLIENT_dict["wpaKeyMgmt"]
            testvars_lan["lan.wpaCipher"].value  = CLIENT_dict["wpaCipher"]
            testvars_lan["lan.wpaGroupCipher"].value  = CLIENT_dict["wpaGroupCipher"]
            
            tag_list.append("WLAN")
            tag_list.append("WiFi6")
            tag_list.append("5GHz")

        elif Clients == "WiFi6e (6GHz)":
            print(f"Using WiFi6e (6GHz)  Client ...")

            testvars_lan["lan.lanSSID"].value  = DUT_dict["SSID-6G"]
            testvars_lan["lan.wpaKey"].value  = DUT_dict["WPA"]

            testvars_lan["lan.lanInterface"].value  = CLIENT_dict["lanInterface"]
            testvars_lan["lan.lanSecurity"].value  = CLIENT_dict["lanSecurity"]
            testvars_lan["lan.lanClients"].value  = "1"
            testvars_lan["lan.lanChannel"].value  = CLIENT_dict["lanChannel"]
            testvars_lan["lan.lan80211Phy"].value  = CLIENT_dict["lan80211Phy"]
            testvars_lan["lan.wpaKeyMgmt"].value  = CLIENT_dict["wpaKeyMgmt"]
            testvars_lan["lan.wpaCipher"].value  = CLIENT_dict["wpaCipher"]
            testvars_lan["lan.wpaGroupCipher"].value  = CLIENT_dict["wpaGroupCipher"]
            
            tag_list.append("WLAN")
            tag_list.append("WiFi6e")
            tag_list.append("6GHz")

        elif Clients == "WiFi7 (MLO)":
            print(f"Using WiFi7 (MLO) Client ...")

            testvars_lan["lan.lanSSID"].value  = DUT_dict["SSID-MLO"]
            testvars_lan["lan.wpaKey"].value  = DUT_dict["WPA"]

            testvars_lan["lan.lanInterface"].value  = CLIENT_dict["lanInterface"]
            testvars_lan["lan.lanSecurity"].value  = CLIENT_dict["lanSecurity"]
            testvars_lan["lan.lanClients"].value  = "1"
            testvars_lan["lan.lanChannel"].value  = CLIENT_dict["lanChannel"]
            testvars_lan["lan.lan80211Phy"].value  = CLIENT_dict["lan80211Phy"]
            testvars_lan["lan.wpaKeyMgmt"].value  = CLIENT_dict["wpaKeyMgmt"]
            testvars_lan["lan.wpaCipher"].value  = CLIENT_dict["wpaCipher"]
            testvars_lan["lan.wpaGroupCipher"].value  = CLIENT_dict["wpaGroupCipher"]

            tag_list.append("WLAN")
            tag_list.append("WiFi7")
            tag_list.append("MLO")

        elif Clients == "MULTI":
            print(f"Using multiple Clients ...")
            multi_clients = request.form.getlist("multi_clients")
          
            print(f"Selected clients: {multi_clients}")

            interface_num = 1

            for CLIENT in multi_clients:

                CLIENT_dict = CLIENT_parameters_indexed.loc[:, CLIENT].to_dict()

                def get_interface_name(interface_num):
                    if interface_num == 1:
                        return "lan"
                    return f"lan{interface_num}"

                #current_interface = f"lan{interface_num}"
                current_interface = get_interface_name(interface_num)

                print(f"Updating {CLIENT} -> {current_interface}")

                #print(f"Updating {CLIENT_dict['lanInterface']}... ")

                testvars_lan[f"{current_interface}.lanSSID"].value = DUT_dict["SSID"]
                testvars_lan[f"{current_interface}.wpaKey"].value = DUT_dict["WPA"]

                testvars_lan[f"{current_interface}.lanInterface"].value = CLIENT_dict["lanInterface"]
                testvars_lan[f"{current_interface}.lanClients"].value = CLIENT_dict["lanClients"]
                testvars_lan[f"{current_interface}.lanSecurity"].value = CLIENT_dict["lanSecurity"]
                testvars_lan[f"{current_interface}.lanChannel"].value = CLIENT_dict["lanChannel"]
                testvars_lan[f"{current_interface}.lan80211Phy"].value = CLIENT_dict["lan80211Phy"]
                testvars_lan[f"{current_interface}.wpaKeyMgmt"].value = CLIENT_dict["wpaKeyMgmt"]
                testvars_lan[f"{current_interface}.wpaCipher"].value = CLIENT_dict["wpaCipher"]
                testvars_lan[f"{current_interface}.wpaGroupCipher"].value = CLIENT_dict["wpaGroupCipher"]
                testvars_lan[f"{current_interface}.wpaMode"].value = CLIENT_dict["wpaMode"]
                
                interface_num += 1


                if CLIENT == "LAN":

                    print(f"Updating LAN interface ...")

                    testvars_lan[f"{current_interface}.lanInterface"].value = DUT_dict["LAN"]
                    testvars_lan[f"{current_interface}.lanSSID"].value = ""
                    testvars_lan[f"{current_interface}.wpaKey"].value = ""

                    tag_list.append("LAN")

                if CLIENT == "WiFi4 (2.4GHz)":
                    print(f"Updating WiFi4 (2.4GHz) interface ...")

                    tag_list.append("WLAN")
                    tag_list.append("WiFi4")
                    tag_list.append("2.4GHz")

                if CLIENT == "WiFi5 (5GHz)":
                    print(f"Updating WiFi5 (5GHz) interface ...")

                    tag_list.append("WLAN")
                    tag_list.append("WiFi5")
                    tag_list.append("5GHz")

                if CLIENT == "WiFi6 (2.4GHz)":
                    print(f"Updating WiFi6 (2.4GHz) interface ...")

                    tag_list.append("WLAN")
                    tag_list.append("WiFi6")
                    tag_list.append("2.4GHz")

                if CLIENT == "WiFi6 (5GHz)":
                    print(f"Updating WiFi6 (5GHz) interface ...")

                    tag_list.append("WLAN")
                    tag_list.append("WiFi6")
                    tag_list.append("5GHz")

                if CLIENT == "WiFi6e (6GHz)":
                    print(f"Updating 6GHz interface ...")

                    tag_list.append("WLAN")
                    tag_list.append("WiFi6e")
                    tag_list.append("6GHz")

                if CLIENT == "WiFi7 (MLO)":
#WiFi-7 tri-band adapter
                    print(f"Updating WiFi7 (MLO) interface ...")

                    tag_list.append("WLAN")
                    tag_list.append("WiFi7")
                    tag_list.append("MLO")

# Set testvars for topology
        Topology = selected_options["Topology"]
        if Topology == "MESH":
            testvars_lan["lan.lanBSSID"].value = DUT_dict["AP-MAC-2G"]
            testvars_lan["lan2.lanBSSID"].value = DUT_dict["AP-MAC-2G"]
            testvars_lan["lan3.lanBSSID"].value = DUT_dict["AP-MAC-5G"]
            testvars_lan["lan4.lanBSSID"].value = DUT_dict["AP-MAC-2G"]
            testvars_lan["lan5.lanBSSID"].value = DUT_dict["AP-MAC-5G"]
            testvars_lan["lan7.lanBSSID"].value = DUT_dict["AP-MAC-6G"]
            testvars_lan["lan8.lanBSSID"].value = DUT_dict["AP-MAC-MLO"]
            tag_list.append("MESH")

# Generate config name
        config_name = "Python:"
        config_name = config_name + DUT_dict['GW-NAME'] + "_" + DUT_dict['GW-FIRMWARE'] + "_"
        config_name = config_name + selected_options['WAN Type'] + "_"
        config_name = config_name + selected_options['WAN Mode'] + "_"
        config_name = config_name + selected_options['Topology'] + "_"
        config_name = config_name + selected_options['Clients']
        if selected_options['IPv6'] == "yes":
            config_name = config_name + "_IPv6"
        if selected_options['TR-069'] == "yes":
            config_name = config_name + "_CWMP"
        if selected_options['Reboot'] == "no":
            config_name = config_name + " (NO REBOOT)"
        if len(selected_options['notes']) > 0:
            config_name = config_name + " " + selected_options['notes']
        print(f"Config {config_name}")


# Update config notes
        print(f"Updating notes in {cfg_default.name} ...")
        config_notes = cfg_default.note
        config_notes = config_name + " - " + str(date.today()) + "\n" + config_notes
        c.configs.edit(Config(id='3471', note=config_notes))

# Update config tags
        print(f"Updating tags in config {cfg_default.name} ...")
        c.configs.edit(Config(id='3471', tags=tag_list))

# Create device
        dut_name = DUT_dict['GW-VENDOR'] + "_" + DUT_dict["GW-MODEL"] + "_" + DUT_dict["GW-FIRMWARE"]
        dut_description = "Created by Python"
        if selected_options['Topology'] == "MESH":
            dut_name = dut_name + "_" + DUT_dict["AP-MODEL"] + "_" + DUT_dict["AP-FIRMWARE"]

        try:
            dut_device = c.devices.get_by_name(dut_name)
            if dut_device is not None:
                print(f"Device {dut_name} exists.")
        except:
            dut_device = c.devices.create(Device(name=dut_name, description=dut_description))
            print(f"Device {dut_name} created.")

# Update WAN testvars

        print("Updating WAN testvars...")
        testvars_list = list(testvars_wan.values())
        c.configs.bulk_edit_testvars(3471, testvars_list)

# Update basic testvars
        print("Updating basic testvars...")
        testvars_list = list(testvars_basic.values())
        c.configs.bulk_edit_testvars(3471, testvars_list)

# Update ACS testvars
        print("Updating ACS testvars...")
        testvars_list = list(testvars_acs.values())
        c.configs.bulk_edit_testvars(3471, testvars_list)

# Update LAN testvars
        print("Updating LAN testvars...")
        testvars_list = list(testvars_lan.values())
        c.configs.bulk_edit_testvars(3471, testvars_list)

        print("Finished updating testvars.")

### set package associated device name        

        print(f"DUT Device id: {dut_device.id}")
        print(f"DUT Device name: {dut_device.name}")

        pkg_base = c.packages.get_by_name("Base")
        print(f"Base test package has {pkg_base.test_count} tests")
        tl_base = pkg_base.testlist 

        pkg_sec = c.packages.get_by_name("Security")
        print(f"Security test package has {pkg_sec.test_count} tests")
        tl_sec = pkg_sec.testlist 

        pkg_sanity = c.packages.get_by_name("Sanity check")
        print(f"Sanity test package has {pkg_sanity.test_count} tests")
        tl_sanity = pkg_sanity.testlist

        pkg_perfstab = c.packages.get_by_name("Performance/Stability")
        print(f"Performance/Stability test package has {pkg_perfstab.test_count} tests")
        tl_perfstab = pkg_perfstab.testlist

        pkg_dos = c.packages.get_by_name("DOS")
        print(f"DOS test package has {pkg_dos.test_count} tests")
        tl_dos = pkg_dos.testlist

        pkg_perf = c.packages.get_by_name("Performance")
        print(f"Performance test package has {pkg_perf.test_count} tests")
        tl_perf = pkg_perf.testlist

        pkg_tr69 = c.packages.get_by_name("Mgmt: TR-069")
        print(f"Mgmt: TR-069 test package has {pkg_tr69.test_count} tests")
        tl_tr69 = pkg_tr69.testlist

#get python base package
        pkg = c.packages.get_by_name("Python")
        pkg_opt=pkg.options
        pkg_opt.forever="true"

#set test lists 
        pkg_tag_list = list()
        pkg_tag_list.append("python")

        pkg_option = selected_options["Package"]
        if pkg_option == "Base":
            tl=tl_base
            #pkg_tag="Base"
            pkg_tag_list.append("BASE")
            pkg_opt.forever="false"
        elif pkg_option == "Sanity":
            tl=tl_sanity
            pkg_tag_list.append("SANITY")
            pkg_opt.forever="false"
        elif pkg_option == "Security":
            tl=tl_sec
            pkg_tag_list.append("SECURITY")
            pkg_opt.forever="false"
        elif pkg_option == "Performance":
            tl=tl_perf
            pkg_tag_list.append("PERFORMANCE")
            pkg_opt.forever="false"
        elif pkg_option == "Performance/Stability":
            tl=tl_perfstab
            pkg_tag_list.append("PERFORMANCE")
            pkg_tag_list.append("STABILITY")
            pkg_opt.forever="true"
        elif pkg_option == "DOS":
            tl=tl_dos
            pkg_tag_list.append("DOS")
            pkg_opt.forever="false"
        elif pkg_option == "Performance":
            tl=tl_perf
            pkg_tag_list.append("PERFORMANCE")
            pkg_opt.forever="false"
        elif pkg_option == "Mgmt: TR-069":
            tl=tl_tr69
            pkg_tag_list.append("MGMT")
            pkg_opt.forever="false"

        pkg_notes = pkg_option + " Package" + " - " + str(date.today()) 

        print(f"Updating package {pkg.name} with device {dut_device.name} and adding {pkg_option} testlists...")
        c.packages.edit(Package(id=pkg.id, device_id=dut_device.id, testlist=tl, tags=pkg_tag_list, note=pkg_notes, options=pkg_opt))

        print('Checking config for errors...')
        check = c.configs.check_config(cfg_default.contents)
        if len(check.errors) > 0:
            print('config errors:'.format(pkg.name))
            for e in check.errors:
                print('        {0}'.format(e.error))
                print('')
                continue
        print(f"Launching package {pkg.name} with associated device {dut_device.name}...")
        j = c.jobs.launch(Job(package_id=pkg.id))

# working for job to be assigned a result ID
        print("Running startup procedure. This may take a few minutes...")
        while j.result_id is None:
            time.sleep(1)
            j = c.jobs.get(j.id)

        print('        Result-ID: {0}'.format(j.result_id))
        print('')
        print(f"Package {pkg.name} launched!")

        rslt = c.results.get(j.result_id)
        print(f"Result ID is {rslt.id}")
        print(f"Result Device is {rslt.device_id}")
        print(f"Result Note is {rslt.note}")

        return f"Launched package {pkg.name} with config {config_name}"

    else:
        return render_template('cdrouter_configurator.html', options=options)

@app.route('/get_dut_attributes')
@basic_auth.required
def get_dut_attributes():
    dut = request.args.get("dut")

    if dut not in DUT_parameters_indexed.columns:
        return jsonify({"error": f"Unknown DUT: {dut}"}), 404

    dut_data = (
        DUT_parameters_indexed[dut]
        .where(DUT_parameters_indexed[dut].notna(), None)
        .to_dict()
    )

    return jsonify(dut_data)


app.run(debug=True, port=5000, host='0.0.0.0')



